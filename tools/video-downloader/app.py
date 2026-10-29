"""Free video downloader GUI: paste a URL, pick a quality (up to 4K/8K), download."""

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
        self.geometry("640x330")
        self.minsize(520, 330)
        self.options = []

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

        self.title_lbl = ttk.Label(frm, text="", wraplength=580, font=("", 10, "bold"))
        self.title_lbl.grid(row=1, column=0, columnspan=3, sticky="w", **pad)

        ttk.Label(frm, text="Quality:").grid(row=2, column=0, sticky="w", **pad)
        self.quality = ttk.Combobox(frm, state="readonly")
        self.quality.grid(row=2, column=1, sticky="ew", **pad)
        self.container = ttk.Combobox(frm, state="readonly", values=["mp4", "mkv"], width=6)
        self.container.set("mp4")
        self.container.grid(row=2, column=2, **pad)

        ttk.Label(frm, text="Save to:").grid(row=3, column=0, sticky="w", **pad)
        self.out_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(frm, textvariable=self.out_dir).grid(row=3, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse", command=self.browse).grid(row=3, column=2, **pad)

        self.bar = ttk.Progressbar(frm, maximum=100)
        self.bar.grid(row=4, column=0, columnspan=3, sticky="ew", **pad)
        self.status = ttk.Label(frm, text="Paste a YouTube (or other site) link and click Fetch.")
        self.status.grid(row=5, column=0, columnspan=3, sticky="w", **pad)

        btns = ttk.Frame(frm)
        btns.grid(row=6, column=0, columnspan=3, **pad)
        self.dl_btn = ttk.Button(btns, text="Download", command=self.download, state="disabled")
        self.dl_btn.pack(side="left", padx=5)
        ttk.Button(btns, text="Open folder", command=self.open_folder).pack(side="left", padx=5)

        if not core.ffmpeg_location():
            self.status.config(text="Warning: ffmpeg not found - 1080p+ and MP3 need it (see README).")

    # Tk widgets must only be touched from the main thread.
    def ui(self, fn, *args):
        self.after(0, fn, *args)

    def set_status(self, text):
        self.status.config(text=text)

    def paste_and_fetch(self):
        try:
            clip = self.clipboard_get().strip()
            if clip.startswith("http"):
                self.url.set(clip)
        except tk.TclError:
            pass
        self.fetch()

    def fetch(self):
        url = self.url.get().strip()
        if not url:
            return
        self.fetch_btn.config(state="disabled")
        self.dl_btn.config(state="disabled")
        self.set_status("Fetching available qualities...")
        threading.Thread(target=self._fetch, args=(url,), daemon=True).start()

    def _fetch(self, url):
        try:
            title, duration, options = core.fetch_info(url)
            self.ui(self._fetched, title, duration, options)
        except Exception as e:
            self.ui(self._failed, f"Could not read this link:\n{e}")

    def _fetched(self, title, duration, options):
        self.options = options
        mins = f"  ({int(duration) // 60}:{int(duration) % 60:02d})" if duration else ""
        self.title_lbl.config(text=title + mins)
        self.quality.config(values=[o.label for o in options])
        self.quality.current(0)  # highest quality first
        self.fetch_btn.config(state="normal")
        self.dl_btn.config(state="normal")
        self.set_status(f"{len(options)} options found. Highest quality is selected.")

    def _failed(self, msg):
        self.fetch_btn.config(state="normal")
        self.dl_btn.config(state="normal" if self.options else "disabled")
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
        if not self.options:
            return
        option = self.options[self.quality.current()]
        out_dir = self.out_dir.get()
        os.makedirs(out_dir, exist_ok=True)
        self.dl_btn.config(state="disabled")
        self.fetch_btn.config(state="disabled")
        self.bar["value"] = 0
        args = (self.url.get().strip(), option, out_dir, self.container.get())
        threading.Thread(target=self._download, args=args, daemon=True).start()

    def _download(self, url, option, out_dir, container):
        def progress(pct, text):
            self.ui(self.bar.config, {"value": pct})
            self.ui(self.set_status, text)
        try:
            core.download(url, option, out_dir, container, progress)
            self.ui(self._done)
        except Exception as e:
            self.ui(self._failed, f"Download failed:\n{e}")

    def _done(self):
        self.bar["value"] = 100
        self.set_status("Download complete!")
        self.fetch_btn.config(state="normal")
        self.dl_btn.config(state="normal")


if __name__ == "__main__":
    App().mainloop()
