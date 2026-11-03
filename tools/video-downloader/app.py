"""Free video downloader GUI: paste a URL, pick a quality (up to 4K/8K), download.

Handles single videos and playlists from YouTube and 1000+ other sites.
"""

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import core


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free Video Downloader")
        self.geometry("660x460")
        self.minsize(540, 460)
        self.info = None
        self.info_url = None

        pad = {"padx": 10, "pady": 5}
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Video URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url = tk.StringVar()
        entry = ttk.Entry(frm, textvariable=self.url)
        entry.grid(row=0, column=1, sticky="ew", **pad)
        entry.bind("<Return>", lambda e: self.fetch())
        self.fetch_btn = ttk.Button(frm, text="Paste & Fetch", command=self.paste_and_fetch)
        self.fetch_btn.grid(row=0, column=2, **pad)

        self.title_lbl = ttk.Label(frm, text="", wraplength=600, font=("", 10, "bold"))
        self.title_lbl.grid(row=1, column=0, columnspan=3, sticky="w", **pad)

        # Shown only when the link is (or belongs to) a playlist.
        self.pl_frame = ttk.Frame(frm)
        self.pl_frame.grid(row=2, column=0, columnspan=3, sticky="w", **pad)
        self.pl_frame.grid_remove()
        self.whole_playlist = tk.BooleanVar()
        self.pl_check = ttk.Checkbutton(self.pl_frame, text="Download full playlist",
                                        variable=self.whole_playlist, command=self.toggle_playlist)
        self.pl_check.pack(side="left")
        self.items_lbl = ttk.Label(self.pl_frame, text="   Videos (e.g. 1-10, blank = all):")
        self.items = tk.StringVar()
        self.items_entry = ttk.Entry(self.pl_frame, textvariable=self.items, width=12)

        ttk.Label(frm, text="Quality:").grid(row=3, column=0, sticky="w", **pad)
        self.quality = ttk.Combobox(frm, state="readonly")
        self.quality.grid(row=3, column=1, sticky="ew", **pad)
        self.container = ttk.Combobox(frm, state="readonly", values=["mp4", "mkv"], width=6)
        self.container.set("mp4")
        self.container.grid(row=3, column=2, **pad)

        ttk.Label(frm, text="Save to:").grid(row=4, column=0, sticky="w", **pad)
        self.out_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(frm, textvariable=self.out_dir).grid(row=4, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse", command=self.browse).grid(row=4, column=2, **pad)

        # For private / login-only videos: reuse the login saved in a browser.
        ttk.Label(frm, text="Use login from:").grid(row=5, column=0, sticky="w", **pad)
        self.browser = ttk.Combobox(frm, state="readonly", width=14,
                                    values=["None"] + [b.title() for b in core.BROWSERS])
        self.browser.set("None")
        self.browser.grid(row=5, column=1, sticky="w", **pad)

        self.bar = ttk.Progressbar(frm, maximum=100)
        self.bar.grid(row=6, column=0, columnspan=3, sticky="ew", **pad)
        self.status = ttk.Label(frm, text="Paste a video or playlist link and click Fetch.",
                                wraplength=600)
        self.status.grid(row=7, column=0, columnspan=3, sticky="w", **pad)

        btns = ttk.Frame(frm)
        btns.grid(row=8, column=0, columnspan=3, **pad)
        self.dl_btn = ttk.Button(btns, text="Download", command=self.download, state="disabled")
        self.dl_btn.pack(side="left", padx=5)
        ttk.Button(btns, text="Open folder", command=self.open_folder).pack(side="left", padx=5)

        ttk.Label(frm, text="Works with: " + ", ".join(core.POPULAR_SITES) + " and 1000+ more",
                  foreground="gray", wraplength=600).grid(row=9, column=0, columnspan=3,
                                                          sticky="w", **pad)

        if not core.ffmpeg_location():
            self.status.config(text="Warning: ffmpeg not found - 1080p+ and MP3 need it (see README).")

    # Tk widgets must only be touched from the main thread.
    def ui(self, fn, *args):
        self.after(0, fn, *args)

    def login_browser(self):
        b = self.browser.get()
        return None if b == "None" else b.lower()

    def set_status(self, text):
        self.status.config(text=text)

    def busy(self, on):
        self.fetch_btn.config(state="disabled" if on else "normal")
        self.pl_check.config(state="disabled" if on else "normal")
        self.dl_btn.config(state="disabled" if on or not self.info else "normal")

    def paste_and_fetch(self):
        try:
            clip = self.clipboard_get().strip()
            if clip.startswith("http"):
                self.url.set(clip)
        except tk.TclError:
            pass
        self.fetch()

    def fetch(self, playlist=False):
        url = self.url.get().strip()
        if not url:
            return
        self.info = None
        self.busy(True)
        self.set_status("Reading playlist..." if playlist else "Fetching available qualities...")
        args = (url, playlist, self.login_browser())
        threading.Thread(target=self._fetch, args=args, daemon=True).start()

    def toggle_playlist(self):
        self.fetch(self.whole_playlist.get())

    def _fetch(self, url, playlist, browser):
        try:
            self.ui(self._fetched, url, core.fetch_info(url, playlist, browser))
        except Exception as e:
            self.ui(self._failed, f"Could not read this link:\n{core.friendly_error(e)}")

    def _fetched(self, url, info):
        self.info, self.info_url = info, url
        if info.is_playlist:
            self.title_lbl.config(text=f"Playlist: {info.title}  ({len(info.entries)} videos)")
        else:
            d = info.duration
            mins = f"  ({int(d) // 60}:{int(d) % 60:02d})" if d else ""
            self.title_lbl.config(text=info.title + mins)

        if info.is_playlist or info.has_playlist:
            self.whole_playlist.set(info.is_playlist)
            self.pl_frame.grid()
            if info.is_playlist:
                self.items_lbl.pack(side="left")
                self.items_entry.pack(side="left")
            else:
                self.items_lbl.pack_forget()
                self.items_entry.pack_forget()
        else:
            self.pl_frame.grid_remove()
        self.items.set("")

        self.quality.config(values=[o.label for o in info.options])
        self.quality.current(0)  # highest quality first
        self.busy(False)
        if info.is_playlist:
            self.set_status("Pick a quality; each video downloads at the best quality up to it.")
        elif info.has_playlist:
            self.set_status("This video is part of a playlist - tick the box to download all of it.")
        else:
            self.set_status(f"{len(info.options)} options found. Highest quality is selected.")

    def _failed(self, msg):
        self.busy(False)
        self.set_status("Error.")
        messagebox.showerror("Error", msg)

    def browse(self):
        d = filedialog.askdirectory(initialdir=self.out_dir.get())
        if d:
            self.out_dir.set(d)

    def open_folder(self):
        d = self.out_dir.get()
        if os.name == "nt":
            os.startfile(d)
        else:
            import subprocess
            import sys
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", d])

    def download(self):
        if not self.info:
            return
        if self.url.get().strip() != self.info_url:
            # The link was edited after fetching; fetch the new one first.
            self.fetch()
            return
        items = self.items.get() if self.info.is_playlist else ""
        if not core.valid_items(items):
            messagebox.showerror("Error", "Videos should look like 1-10 or 1,3,5-7.")
            return
        option = self.info.options[self.quality.current()]
        out_dir = self.out_dir.get()
        os.makedirs(out_dir, exist_ok=True)
        self.busy(True)
        self.dl_btn.config(state="disabled")
        self.bar["value"] = 0
        args = (self.info_url, option, out_dir, self.container.get(), self.info.is_playlist, items,
                self.login_browser())
        threading.Thread(target=self._download, args=args, daemon=True).start()

    def _download(self, url, option, out_dir, container, playlist, items, browser):
        def progress(pct, text):
            self.ui(self.bar.config, {"value": pct})
            self.ui(self.set_status, text)
        try:
            failed = core.download(url, option, out_dir, container, progress, playlist, items,
                                   browser)
            self.ui(self._done, failed)
        except Exception as e:
            self.ui(self._failed, f"Download failed:\n{core.friendly_error(e)}")

    def _done(self, failed):
        self.bar["value"] = 100
        self.set_status("Download complete!" + (
            " Some videos were skipped (private, deleted or blocked)." if failed else ""))
        self.busy(False)


if __name__ == "__main__":
    App().mainloop()
