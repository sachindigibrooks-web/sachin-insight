"""Free video downloader GUI: paste a URL, pick a quality (up to 4K/8K), download.

Handles single videos and playlists from YouTube and 1000+ other sites, plus
extras: clip a part, skip sponsors, a data limit, AI subtitles in many
languages, WhatsApp-sized copies, and an IDM-style clipboard watcher.
"""

import os
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import core
import extras

URL_RE = re.compile(r"^https?://\S+$")
SUB_MODES = {"Add to video (can turn on/off)": "embed", "Burn into the picture": "burn",
             "Only a .srt file": "srt"}
AI_CHOICES = {"Accurate (slower)": "accurate", "Fast": "fast"}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free Video Downloader")
        self.minsize(560, 470)
        self.info = None
        self.info_url = None
        self.working = False
        self.auto = False  # download as soon as the fetch finishes (clipboard / queue)
        self.queue = []  # links waiting while a download runs
        self.extractors = None
        self.last_clip = self.read_clipboard()

        pad = {"padx": 10, "pady": 4}
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

        self.more_btn = ttk.Button(frm, command=self.toggle_more)
        self.more_btn.grid(row=6, column=0, columnspan=3, sticky="w", **pad)
        self.more = self.build_more(frm)
        self.more.grid(row=7, column=0, columnspan=3, sticky="ew", **pad)
        self.toggle_more()  # start collapsed

        self.bar = ttk.Progressbar(frm, maximum=100)
        self.bar.grid(row=8, column=0, columnspan=3, sticky="ew", **pad)
        self.status = ttk.Label(frm, text="Paste a video or playlist link and click Fetch.",
                                wraplength=600)
        self.status.grid(row=9, column=0, columnspan=3, sticky="w", **pad)

        btns = ttk.Frame(frm)
        btns.grid(row=10, column=0, columnspan=3, **pad)
        self.dl_btn = ttk.Button(btns, text="Download", command=self.download, state="disabled")
        self.dl_btn.pack(side="left", padx=5)
        ttk.Button(btns, text="Open folder", command=self.open_folder).pack(side="left", padx=5)
        self.watch = tk.BooleanVar(value=True)
        ttk.Checkbutton(btns, text="Watch clipboard (popup when a video link is copied)",
                        variable=self.watch).pack(side="left", padx=10)

        ttk.Label(frm, text="Works with: " + ", ".join(core.POPULAR_SITES) + " and 1000+ more",
                  foreground="gray", wraplength=600).grid(row=11, column=0, columnspan=3,
                                                          sticky="w", **pad)

        if not core.ffmpeg_location():
            self.status.config(text="Warning: ffmpeg not found - 1080p+ and MP3 need it (see README).")
        threading.Thread(target=self.load_extractors, daemon=True).start()
        self.after(1000, self.poll_clipboard)

    def build_more(self, parent):
        box = ttk.LabelFrame(parent, text="More options")
        pad = {"padx": 8, "pady": 3}
        box.columnconfigure(1, weight=1)

        ttk.Label(box, text="Clip only:").grid(row=0, column=0, sticky="w", **pad)
        clip = ttk.Frame(box)
        clip.grid(row=0, column=1, sticky="w", **pad)
        self.clip_start, self.clip_end = tk.StringVar(), tk.StringVar()
        ttk.Label(clip, text="from").pack(side="left")
        ttk.Entry(clip, textvariable=self.clip_start, width=9).pack(side="left", padx=4)
        ttk.Label(clip, text="to").pack(side="left")
        ttk.Entry(clip, textvariable=self.clip_end, width=9).pack(side="left", padx=4)
        ttk.Label(clip, text="e.g. 1:20:00  (empty = full video)", foreground="gray").pack(
            side="left", padx=4)

        self.sponsor = tk.BooleanVar()
        ttk.Checkbutton(box, text="Skip sponsors, intros, outros and 'subscribe' reminders "
                                  "(YouTube)", variable=self.sponsor).grid(
            row=1, column=0, columnspan=2, sticky="w", **pad)

        ttk.Label(box, text="Data limit:").grid(row=2, column=0, sticky="w", **pad)
        lim = ttk.Frame(box)
        lim.grid(row=2, column=1, sticky="w", **pad)
        self.budget = tk.StringVar()
        ttk.Entry(lim, textvariable=self.budget, width=8).pack(side="left")
        ttk.Label(lim, text="MB  - picks the best quality that fits (playlist: total size)",
                  foreground="gray").pack(side="left", padx=4)
        self.budget.trace_add("write", lambda *a: self.apply_budget())
        self.clip_start.trace_add("write", lambda *a: self.apply_budget())
        self.clip_end.trace_add("write", lambda *a: self.apply_budget())

        ttk.Label(box, text="Subtitles (AI):").grid(row=3, column=0, sticky="w", **pad)
        subs = ttk.Frame(box)
        subs.grid(row=3, column=1, sticky="w", **pad)
        self.sub_lang = ttk.Combobox(subs, state="readonly", width=17, values=
                                     ["Off", "Original language"] + [n for n, _, _ in extras.LANGUAGES])
        self.sub_lang.set("Off")
        self.sub_lang.pack(side="left")
        self.sub_mode = ttk.Combobox(subs, state="readonly", width=27, values=list(SUB_MODES))
        self.sub_mode.current(0)
        self.sub_mode.pack(side="left", padx=4)
        self.ai_model = ttk.Combobox(subs, state="readonly", width=15, values=list(AI_CHOICES))
        self.ai_model.current(0)
        self.ai_model.pack(side="left")

        ttk.Label(box, text="WhatsApp copy:").grid(row=4, column=0, sticky="w", **pad)
        self.whatsapp = ttk.Combobox(box, state="readonly", width=12,
                                     values=["Off"] + [f"{n} MB" for n in extras.WHATSAPP_SIZES])
        self.whatsapp.set("Off")
        self.whatsapp.grid(row=4, column=1, sticky="w", **pad)
        return box

    def toggle_more(self):
        if self.more.winfo_ismapped() or not hasattr(self, "_more_init"):
            self._more_init = True
            self.more.grid_remove()
            self.more_btn.config(text="▸ More options: clip, skip sponsors, data limit, "
                                      "AI subtitles, WhatsApp")
        else:
            self.more.grid()
            self.more_btn.config(text="▾ Hide more options")

    # Tk widgets must only be touched from the main thread.
    def ui(self, fn, *args):
        self.after(0, fn, *args)

    def login_browser(self):
        b = self.browser.get()
        return None if b == "None" else b.lower()

    def set_status(self, text):
        self.status.config(text=text)

    def busy(self, on):
        self.working = on
        self.fetch_btn.config(state="disabled" if on else "normal")
        self.pl_check.config(state="disabled" if on else "normal")
        self.dl_btn.config(state="disabled" if on or not self.info else "normal")

    # ------------------------------------------------------------ clipboard watcher

    def read_clipboard(self):
        try:
            return self.clipboard_get().strip()
        except tk.TclError:  # empty, or not text
            return ""

    def load_extractors(self):
        from yt_dlp.extractor import gen_extractor_classes
        self.extractors = [ie for ie in gen_extractor_classes() if ie.ie_key() != "Generic"]

    def is_video_link(self, text):
        if not URL_RE.match(text) or self.extractors is None:
            return False
        return any(ie.suitable(text) for ie in self.extractors)

    def poll_clipboard(self):
        clip = self.read_clipboard()
        if clip != self.last_clip:
            self.last_clip = clip
            if self.watch.get() and clip != self.url.get().strip() and self.is_video_link(clip):
                self.popup(clip)
        self.after(1000, self.poll_clipboard)

    def popup(self, link):
        win = tk.Toplevel(self)
        win.title("Video link copied")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        body = ttk.Frame(win, padding=12)
        body.pack(fill="both")
        ttk.Label(body, text="Video link copied - download it?", font=("", 10, "bold")).pack(
            anchor="w")
        ttk.Label(body, text=link if len(link) < 60 else link[:57] + "...",
                  foreground="gray").pack(anchor="w", pady=(2, 8))
        row = ttk.Frame(body)
        row.pack(anchor="e")

        def act(auto):
            win.destroy()
            self.take_link(link, auto)

        ttk.Button(row, text="Download (best quality)", command=lambda: act(True)).pack(
            side="left", padx=3)
        ttk.Button(row, text="Choose quality...", command=lambda: act(False)).pack(
            side="left", padx=3)
        ttk.Button(row, text="Ignore", command=win.destroy).pack(side="left", padx=3)
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        win.geometry(f"+{win.winfo_screenwidth() - w - 24}+{win.winfo_screenheight() - h - 80}")
        win.after(20000, lambda: win.winfo_exists() and win.destroy())

    def take_link(self, link, auto):
        if self.working:
            self.queue.append(link)
            self.set_status(f"Added to queue ({len(self.queue)} waiting). It starts after the "
                            "current download.")
            return
        self.deiconify()
        self.lift()
        self.focus_force()
        self.url.set(link)
        self.auto = auto
        self.fetch()

    def next_in_queue(self):
        if self.queue and not self.working:
            self.url.set(self.queue.pop(0))
            self.auto = True
            self.fetch()

    # ------------------------------------------------------------ fetch

    def paste_and_fetch(self):
        clip = self.read_clipboard()
        if clip.startswith("http"):
            self.url.set(clip)
            self.last_clip = clip  # don't also pop up for it
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
        self.apply_budget()
        if self.auto:
            self.auto = False
            self.download()

    def clip_fraction(self):
        """Share of the video the clip covers (1 when not clipping or unknown)."""
        d = self.info.duration if self.info else None
        try:
            start = core.parse_time(self.clip_start.get()) or 0
            end = core.parse_time(self.clip_end.get())
        except ValueError:
            return 1
        if not d or (not start and end is None):
            return 1
        return max(0.0, min(end if end is not None else d, d) - start) / d

    def apply_budget(self):
        """With a data limit, select the best single-video quality that fits it."""
        if not self.info or self.info.is_playlist:
            return
        try:
            limit = float(self.budget.get()) * 1e6
        except ValueError:
            return
        frac = self.clip_fraction()
        videos = [(i, o) for i, o in enumerate(self.info.options) if not o.audio_only and o.size]
        for i, o in videos:
            if o.size * frac <= limit:
                self.quality.current(i)
                self.set_status(f"Data limit: {o.label.split('~')[0].strip()} fits "
                                f"(~{core.human_size(o.size * frac)}).")
                return
        if videos:
            i, o = videos[-1]
            self.quality.current(i)
            self.set_status(f"Nothing fits in {self.budget.get()} MB; the smallest is "
                            f"~{core.human_size(o.size * frac)}. Try audio only or a clip.")

    def _failed(self, msg):
        self.busy(False)
        self.auto = False
        self.set_status("Error.")
        messagebox.showerror("Error", msg)
        self.next_in_queue()

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

    # ------------------------------------------------------------ download

    def read_extras(self):
        budget = self.budget.get().strip()
        lang = self.sub_lang.get()
        codes = {n: c for n, c, _ in extras.LANGUAGES}
        wa = self.whatsapp.get()
        return core.Extras(
            start=core.parse_time(self.clip_start.get()),
            end=core.parse_time(self.clip_end.get()),
            sponsorblock=self.sponsor.get(),
            budget_mb=float(budget) if budget else None,
            subs_lang=None if lang == "Off" else extras.ORIGINAL if lang == "Original language"
            else codes[lang],
            subs_mode=SUB_MODES[self.sub_mode.get()],
            ai_model=AI_CHOICES[self.ai_model.get()],
            whatsapp_mb=None if wa == "Off" else int(wa.split()[0]))

    def download(self):
        if not self.info:
            return
        if self.url.get().strip() != self.info_url:
            # The link was edited after fetching; fetch the new one first.
            self.fetch()
            return
        items = self.items.get() if self.info.is_playlist else ""
        try:
            if not core.valid_items(items):
                raise ValueError("Videos should look like 1-10 or 1,3,5-7.")
            x = self.read_extras()
        except ValueError as e:
            messagebox.showerror("Error", str(e) if "could not" not in str(e) else
                                 "Data limit should be a number of MB, like 500.")
            return
        option = self.info.options[self.quality.current()]
        out_dir = self.out_dir.get()
        os.makedirs(out_dir, exist_ok=True)
        self.busy(True)
        self.bar["value"] = 0
        args = (self.info_url, option, out_dir, self.container.get(), self.info.is_playlist, items,
                self.login_browser(), x, len(self.info.entries))
        threading.Thread(target=self._download, args=args, daemon=True).start()

    def _download(self, url, option, out_dir, container, playlist, items, browser, x, size):
        def progress(pct, text):
            self.ui(self.bar.config, {"value": pct})
            self.ui(self.set_status, text)
        try:
            res = core.download(url, option, out_dir, container, progress, playlist, items,
                                browser, x, size)
            self.ui(self._done, res)
        except Exception as e:
            self.ui(self._failed, f"Download failed:\n{core.friendly_error(e)}")

    def _done(self, res):
        self.bar["value"] = 100
        msg = "Download complete!"
        if res.failed:
            msg += " Some videos were skipped (private, deleted or blocked)."
        self.set_status(msg + (f" {len(res.warnings)} extra step(s) failed." if res.warnings else ""))
        self.busy(False)
        if res.warnings:
            messagebox.showwarning("Some extras failed", "\n\n".join(res.warnings[:5]))
        self.next_in_queue()


if __name__ == "__main__":
    App().mainloop()
