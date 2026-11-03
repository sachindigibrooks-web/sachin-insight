"""Free video & photo downloader GUI: paste a URL, pick a quality (up to 4K/8K), download.

Handles single videos and playlists from YouTube and 1000+ other sites, photo
posts and galleries (Instagram, Pinterest, X, ...), plus extras: clip a part,
skip sponsors, a data limit, AI subtitles in many languages, WhatsApp-sized
copies, ringtones, an IDM-style clipboard watcher, download history, search
inside videos, followed channels, a phone / website mode with a QR code, a
Hindi interface and self-updating site engines.
"""

import updater

updater.apply()  # use newer site engines downloaded earlier - before anything imports them

import os  # noqa: E402
import re  # noqa: E402
import threading  # noqa: E402
import tkinter as tk  # noqa: E402
from pathlib import Path  # noqa: E402
from tkinter import filedialog, messagebox, ttk  # noqa: E402

import appdata  # noqa: E402
import core  # noqa: E402
import extras  # noqa: E402
import follows  # noqa: E402
import history  # noqa: E402
import i18n  # noqa: E402
import photos  # noqa: E402
import windows  # noqa: E402

URL_RE = re.compile(r"^https?://\S+$")
SUB_MODES = ["embed", "burn", "srt"]
SUB_MODE_KEYS = ["mode_embed", "mode_burn", "mode_srt"]
AI_MODELS = ["accurate", "fast"]
AI_KEYS = ["ai_accurate", "ai_fast"]
FOLLOW_TICK = 5 * 60 * 1000  # look for due follows every 5 minutes (each is checked hourly)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = appdata.setting("lang", "en")
        self.minsize(600, 500)
        self.info = None
        self.info_url = None
        self.photo_mode = False  # the fetched link is a photo post / gallery
        self.working = False
        self.follow_running = False
        self.auto = False  # download as soon as the fetch finishes (clipboard / queue)
        self.queue = []  # links waiting while a download runs
        self.extractors = None
        self.last_clip = self.read_clipboard()
        self.texts = []  # (widget, key) pairs re-labelled when the language changes
        self.status_text = ""
        self.status_key = None  # set when the status is a fixed UI text (re-labelled on toggle)

        pad = {"padx": 10, "pady": 4}
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(8, 0))
        for key, cmd in (("history", lambda: windows.HistoryWindow(self)),
                         ("search_videos", lambda: windows.SearchWindow(self)),
                         ("follows", lambda: windows.FollowsWindow(self)),
                         ("phone", lambda: windows.PhoneWindow(self)),
                         ("updates", self.check_updates)):
            self.label(ttk.Button(bar, command=cmd), key).pack(side="left", padx=(0, 6))
        self.label(ttk.Button(bar, command=self.toggle_language), "language").pack(side="right")

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=6)
        frm.columnconfigure(1, weight=1)

        self.label(ttk.Label(frm), "url").grid(row=0, column=0, sticky="w", **pad)
        self.url = tk.StringVar()
        entry = ttk.Entry(frm, textvariable=self.url)
        entry.grid(row=0, column=1, sticky="ew", **pad)
        entry.bind("<Return>", lambda e: self.fetch())
        self.fetch_btn = self.label(ttk.Button(frm, command=self.paste_and_fetch), "fetch")
        self.fetch_btn.grid(row=0, column=2, **pad)

        self.title_lbl = ttk.Label(frm, text="", wraplength=620, font=("", 10, "bold"))
        self.title_lbl.grid(row=1, column=0, columnspan=3, sticky="w", **pad)

        # Shown only when the link is (or belongs to) a playlist, or is a photo gallery.
        self.pl_frame = ttk.Frame(frm)
        self.pl_frame.grid(row=2, column=0, columnspan=3, sticky="w", **pad)
        self.pl_frame.grid_remove()
        self.whole_playlist = tk.BooleanVar()
        self.pl_check = self.label(ttk.Checkbutton(self.pl_frame, variable=self.whole_playlist,
                                                   command=self.toggle_playlist), "whole_playlist")
        self.pl_check.pack(side="left")
        self.items_lbl = ttk.Label(self.pl_frame)
        self.items = tk.StringVar()
        self.items_entry = ttk.Entry(self.pl_frame, textvariable=self.items, width=12)

        self.label(ttk.Label(frm), "quality").grid(row=3, column=0, sticky="w", **pad)
        self.quality = ttk.Combobox(frm, state="readonly")
        self.quality.grid(row=3, column=1, sticky="ew", **pad)
        self.container = ttk.Combobox(frm, state="readonly", values=["mp4", "mkv"], width=6)
        self.container.set("mp4")
        self.container.grid(row=3, column=2, **pad)

        self.label(ttk.Label(frm), "save_to").grid(row=4, column=0, sticky="w", **pad)
        self.out_dir = tk.StringVar(value=appdata.setting("out_dir", str(Path.home() / "Downloads")))
        ttk.Entry(frm, textvariable=self.out_dir).grid(row=4, column=1, sticky="ew", **pad)
        self.label(ttk.Button(frm, command=self.browse), "browse").grid(row=4, column=2, **pad)

        # For private / login-only videos: reuse the login saved in a browser.
        self.label(ttk.Label(frm), "login").grid(row=5, column=0, sticky="w", **pad)
        self.browser = ttk.Combobox(frm, state="readonly", width=14)
        self.browser.grid(row=5, column=1, sticky="w", **pad)

        self.more_btn = ttk.Button(frm, command=self.toggle_more)
        self.more_btn.grid(row=6, column=0, columnspan=3, sticky="w", **pad)
        self.more = self.build_more(frm)
        self.more.grid(row=7, column=0, columnspan=3, sticky="ew", **pad)
        self.more.grid_remove()  # start collapsed

        self.bar = ttk.Progressbar(frm, maximum=100)
        self.bar.grid(row=8, column=0, columnspan=3, sticky="ew", **pad)
        self.status = ttk.Label(frm, wraplength=620)
        self.status.grid(row=9, column=0, columnspan=3, sticky="w", **pad)
        self.note = ttk.Label(frm, foreground="#1a7f4b", wraplength=620)  # follows / updates
        self.note.grid(row=10, column=0, columnspan=3, sticky="w", padx=10)

        btns = ttk.Frame(frm)
        btns.grid(row=11, column=0, columnspan=3, **pad)
        self.dl_btn = self.label(ttk.Button(btns, command=self.download, state="disabled"),
                                 "download")
        self.dl_btn.pack(side="left", padx=5)
        self.label(ttk.Button(btns, command=self.open_folder), "open_folder").pack(side="left",
                                                                                     padx=5)
        self.watch = tk.BooleanVar(value=True)
        self.label(ttk.Checkbutton(btns, variable=self.watch), "watch").pack(side="left", padx=10)

        self.sites = ttk.Label(frm, foreground="gray", wraplength=620)
        self.sites.grid(row=12, column=0, columnspan=3, sticky="w", **pad)
        self.label(ttk.Label(frm, font=("", 10, "bold")), "credit").grid(
            row=13, column=0, columnspan=3, pady=(4, 0))

        self.apply_language()
        self.set_status("start")
        if not core.ffmpeg_location():
            self.set_status("Warning: ffmpeg not found - 1080p+ and MP3 need it (see README).")
        threading.Thread(target=self.load_extractors, daemon=True).start()
        threading.Thread(target=self.auto_update, daemon=True).start()
        self.after(1000, self.poll_clipboard)
        self.after(20 * 1000, self.follow_tick)

    # ------------------------------------------------------------ language

    def t(self, key):
        return i18n.ui(key, self.lang)

    def label(self, widget, key):
        """Give `widget` the text for `key` now and whenever the language changes."""
        self.texts.append((widget, key))
        widget.config(text=self.t(key))
        return widget

    def toggle_language(self):
        self.lang = "en" if self.lang == "hi" else "hi"
        appdata.set_setting("lang", self.lang)
        self.apply_language()

    def apply_language(self):
        self.title(f"{self.t('app_title')}  -  Made by Sachin Samria")
        for widget, key in self.texts:
            widget.config(text=self.t(key))
        self.more_btn.config(text=self.t("more_hide" if self.more.winfo_ismapped() else "more_show"))
        self.more.config(text=self.t("more_box"))
        self.items_lbl.config(text=self.t("items_photos" if self.photo_mode else "items_videos"))
        self.sites.config(text=f"{self.t('videos_from')}: " + ", ".join(core.POPULAR_SITES)
                          + f" {self.t('more_sites')} (1000+).\n{self.t('photos_from')}: "
                          + ", ".join(photos.POPULAR_SITES) + f" {self.t('more_sites')} (300+).")
        self.fill_choices()
        self.set_status(self.status_key or self.status_text)

    def fill_choices(self):
        """(Re)label the drop-downs, keeping what is selected."""
        def refill(box, values):
            i = max(box.current(), 0)
            box.config(values=values)
            box.current(i)
        refill(self.browser, [self.t("none")] + [b.title() for b in core.BROWSERS])
        refill(self.sub_lang, [self.t("off"), self.t("orig_lang")]
               + [i18n.language_name(n, self.lang) for n, _, _ in extras.LANGUAGES])
        refill(self.sub_mode, [self.t(k) for k in SUB_MODE_KEYS])
        refill(self.ai_model, [self.t(k) for k in AI_KEYS])
        refill(self.whatsapp, [self.t("off")] + [f"{n} MB" for n in extras.WHATSAPP_SIZES])

    def build_more(self, parent):
        box = ttk.LabelFrame(parent)
        pad = {"padx": 8, "pady": 3}
        box.columnconfigure(1, weight=1)

        self.label(ttk.Label(box), "clip").grid(row=0, column=0, sticky="w", **pad)
        clip = ttk.Frame(box)
        clip.grid(row=0, column=1, sticky="w", **pad)
        self.clip_start, self.clip_end = tk.StringVar(), tk.StringVar()
        self.label(ttk.Label(clip), "from").pack(side="left")
        ttk.Entry(clip, textvariable=self.clip_start, width=9).pack(side="left", padx=4)
        self.label(ttk.Label(clip), "to").pack(side="left")
        ttk.Entry(clip, textvariable=self.clip_end, width=9).pack(side="left", padx=4)
        self.label(ttk.Label(clip, foreground="gray"), "clip_hint").pack(side="left", padx=4)

        self.sponsor = tk.BooleanVar()
        self.label(ttk.Checkbutton(box, variable=self.sponsor), "sponsor").grid(
            row=1, column=0, columnspan=2, sticky="w", **pad)

        self.label(ttk.Label(box), "limit").grid(row=2, column=0, sticky="w", **pad)
        lim = ttk.Frame(box)
        lim.grid(row=2, column=1, sticky="w", **pad)
        self.budget = tk.StringVar()
        ttk.Entry(lim, textvariable=self.budget, width=8).pack(side="left")
        self.label(ttk.Label(lim, foreground="gray"), "limit_hint").pack(side="left", padx=4)
        self.budget.trace_add("write", lambda *a: self.apply_budget())
        self.clip_start.trace_add("write", lambda *a: self.apply_budget())
        self.clip_end.trace_add("write", lambda *a: self.apply_budget())

        self.label(ttk.Label(box), "subs").grid(row=3, column=0, sticky="w", **pad)
        subs = ttk.Frame(box)
        subs.grid(row=3, column=1, sticky="w", **pad)
        self.sub_lang = ttk.Combobox(subs, state="readonly", width=17)
        self.sub_lang.pack(side="left")
        self.sub_mode = ttk.Combobox(subs, state="readonly", width=27)
        self.sub_mode.pack(side="left", padx=4)
        self.ai_model = ttk.Combobox(subs, state="readonly", width=15)
        self.ai_model.pack(side="left")

        self.label(ttk.Label(box), "whatsapp").grid(row=4, column=0, sticky="w", **pad)
        self.whatsapp = ttk.Combobox(box, state="readonly", width=12)
        self.whatsapp.grid(row=4, column=1, sticky="w", **pad)

        self.label(ttk.Label(box), "ringtone").grid(row=5, column=0, sticky="w", **pad)
        ring = ttk.Frame(box)
        ring.grid(row=5, column=1, sticky="w", **pad)
        self.ring_start = tk.StringVar()
        ttk.Entry(ring, textvariable=self.ring_start, width=9).pack(side="left")
        self.label(ttk.Label(ring, foreground="gray"), "ringtone_hint").pack(side="left", padx=4)

        self.searchable = tk.BooleanVar()
        self.label(ttk.Checkbutton(box, variable=self.searchable), "searchable").grid(
            row=6, column=0, columnspan=2, sticky="w", **pad)
        self.label(ttk.Label(box, foreground="gray", wraplength=600), "ai_note").grid(
            row=7, column=0, columnspan=2, sticky="w", **pad)
        return box

    def toggle_more(self):
        if self.more.winfo_ismapped():
            self.more.grid_remove()
            self.more_btn.config(text=self.t("more_show"))
        else:
            self.more.grid()
            self.more_btn.config(text=self.t("more_hide"))

    # Tk widgets must only be touched from the main thread.
    def ui(self, fn, *args):
        self.after(0, fn, *args)

    def login_browser(self):
        i = self.browser.current()
        return core.BROWSERS[i - 1] if i > 0 else None

    def set_status(self, text):
        """Show a status message (English in; shown in the chosen language)."""
        self.status_key = text if text in i18n.UI else None
        self.status_text = self.t(text) if self.status_key else text
        self.status.config(text=i18n.text(self.status_text, self.lang))

    def show_error(self, message):
        messagebox.showerror("Error", i18n.text(message, self.lang), parent=self)

    def busy(self, on):
        self.working = on
        self.fetch_btn.config(state="disabled" if on else "normal")
        self.pl_check.config(state="disabled" if on else "normal")
        self.dl_btn.config(state="disabled" if on or not self.info else "normal")

    # ------------------------------------------------------------ updates

    def auto_update(self):
        updated = updater.check(log=lambda m: None)
        if updated:
            self.ui(self.note.config, {"text": "Site engines updated (" + ", ".join(updated)
                                       + ") - restart the app to use them."})

    def check_updates(self):
        self.note.config(text="Checking for updates...")

        def run():
            updated = updater.check(force=True)
            versions = ", ".join(f"{k} {v}" for k, v in updater.running_versions().items())
            msg = (f"Updated: {', '.join(updated)} - restart the app to use them."
                   if updated else f"Everything is up to date ({versions}).")
            self.ui(self.note.config, {"text": msg})
        threading.Thread(target=run, daemon=True).start()

    # ------------------------------------------------------------ follows

    def follow_tick(self):
        """Every few minutes: check followed channels that are due, one at a time."""
        self.after(FOLLOW_TICK, self.follow_tick)
        if self.follow_running or self.working:
            return
        due = follows.due()
        if not due:
            return
        self.follow_running = True
        args = (due, self.login_browser())  # read widgets here: Tk isn't thread-safe
        threading.Thread(target=self.run_follows, args=args, daemon=True).start()

    def run_follows(self, due, browser):
        total = 0
        for f in due:
            self.ui(self.note.config, {"text": f"Checking followed: {f['title'][:60]}..."})
            try:
                files = follows.check(f, browser=browser)
            except Exception as e:
                self.ui(self.note.config, {"text": f"{f['title'][:40]}: {core.friendly_error(e)}"})
                continue
            if files:
                total += len(files)
                history.add(f["title"], f["url"], files, kind="follow", site=f["site"])
        self.follow_running = False
        if total:
            self.ui(self.note.config, {"text": f"Follows: {total} new file(s) downloaded."})
        else:
            self.ui(self.note.config, {"text": ""})

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
        return any(ie.suitable(text) for ie in self.extractors) or photos.supported(text)

    def poll_clipboard(self):
        clip = self.read_clipboard()
        if clip != self.last_clip:
            self.last_clip = clip
            if self.watch.get() and clip != self.url.get().strip() and self.is_video_link(clip):
                self.popup(clip)
        self.after(1000, self.poll_clipboard)

    def popup(self, link):
        hi = self.lang == "hi"
        win = tk.Toplevel(self)
        win.title("Link copied")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        body = ttk.Frame(win, padding=12)
        body.pack(fill="both")
        ttk.Label(body, text="वीडियो / फोटो लिंक कॉपी हुआ - डाउनलोड करें?" if hi else
                  "Video / photo link copied - download it?", font=("", 10, "bold")).pack(anchor="w")
        ttk.Label(body, text=link if len(link) < 60 else link[:57] + "...",
                  foreground="gray").pack(anchor="w", pady=(2, 8))
        row = ttk.Frame(body)
        row.pack(anchor="e")

        def act(auto):
            win.destroy()
            self.take_link(link, auto)

        ttk.Button(row, text="डाउनलोड (बेस्ट क्वालिटी)" if hi else "Download (best quality)",
                   command=lambda: act(True)).pack(side="left", padx=3)
        ttk.Button(row, text="क्वालिटी चुनें..." if hi else "Choose quality...",
                   command=lambda: act(False)).pack(side="left", padx=3)
        ttk.Button(row, text="रहने दें" if hi else "Ignore", command=win.destroy).pack(
            side="left", padx=3)
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
            return
        except Exception as e:
            video_error = e
        try:  # no video here - maybe a photo post or gallery
            self.ui(self._fetched_photos, url, photos.probe(url, browser))
        except Exception as photo_error:
            self.ui(self._failed, f"Could not read this link:\n{photos.pick_error(video_error, photo_error)}")

    def _fetched_photos(self, url, info):
        self.info, self.info_url, self.photo_mode = info, url, True
        self.title_lbl.config(text=f"Photos: {info.count} found on {info.site}"
                              + (f"  -  {info.title}" if info.title else ""))
        self.pl_frame.grid()
        self.pl_check.pack_forget()
        self.items_lbl.config(text=self.t("items_photos"))
        self.items_lbl.pack(side="left")
        self.items_entry.pack(side="left")
        self.items.set("")
        self.quality.config(values=["Original quality (as uploaded)"])
        self.quality.current(0)
        self.busy(False)
        self.set_status("Photos are saved in a 'Photos' folder inside Save to.")
        if self.auto:
            self.auto = False
            self.download()

    def _fetched(self, url, info):
        self.info, self.info_url, self.photo_mode = info, url, False
        for w in (self.pl_check, self.items_lbl, self.items_entry):
            w.pack_forget()
        self.pl_check.pack(side="left")
        self.items_lbl.config(text=self.t("items_videos"))
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
        if not self.info or self.photo_mode or self.info.is_playlist:
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
        self.show_error(msg)
        self.next_in_queue()

    def browse(self):
        d = filedialog.askdirectory(initialdir=self.out_dir.get())
        if d:
            self.out_dir.set(d)
            appdata.set_setting("out_dir", d)

    def open_folder(self, path=None):
        windows.open_path(path or self.out_dir.get())

    # ------------------------------------------------------------ download

    def read_extras(self):
        budget = self.budget.get().strip()
        li, wi = self.sub_lang.current(), self.whatsapp.current()
        return core.Extras(
            start=core.parse_time(self.clip_start.get()),
            end=core.parse_time(self.clip_end.get()),
            sponsorblock=self.sponsor.get(),
            budget_mb=float(budget) if budget else None,
            subs_lang=None if li <= 0 else extras.ORIGINAL if li == 1
            else extras.LANGUAGES[li - 2][1],
            subs_mode=SUB_MODES[max(self.sub_mode.current(), 0)],
            ai_model=AI_MODELS[max(self.ai_model.current(), 0)],
            whatsapp_mb=extras.WHATSAPP_SIZES[wi - 1] if wi > 0 else None,
            ringtone_start=core.parse_time(self.ring_start.get()),
            searchable=self.searchable.get())

    def download(self):
        if not self.info:
            return
        if self.url.get().strip() != self.info_url:
            # The link was edited after fetching; fetch the new one first.
            self.fetch()
            return
        if self.photo_mode:
            return self.download_photos()
        items = self.items.get() if self.info.is_playlist else ""
        try:
            if not core.valid_items(items):
                raise ValueError("Videos should look like 1-10 or 1,3,5-7.")
            x = self.read_extras()
        except ValueError as e:
            self.show_error(str(e) if "could not" not in str(e) else
                            "Data limit should be a number of MB, like 500.")
            return
        option = self.info.options[self.quality.current()]
        out_dir = self.out_dir.get()
        os.makedirs(out_dir, exist_ok=True)
        self.busy(True)
        self.bar["value"] = 0
        args = (self.info_url, option, out_dir, self.container.get(), self.info.is_playlist, items,
                self.login_browser(), x, len(self.info.entries), self.info.title, self.info.site)
        threading.Thread(target=self._download, args=args, daemon=True).start()

    def progress(self, pct, text):
        self.ui(self.bar.config, {"value": pct})
        self.ui(self.set_status, text)

    def _download(self, url, option, out_dir, container, playlist, items, browser, x, size,
                  title, site):
        try:
            res = core.download(url, option, out_dir, container, self.progress, playlist, items,
                                browser, x, size)
            if res.files:
                history.add(title, url, res.files, "playlist" if playlist else "video", site)
            self.ui(self._done, res)
        except Exception as e:
            self.ui(self._failed, f"Download failed:\n{core.friendly_error(e)}")

    def download_photos(self):
        items = self.items.get().replace(" ", "")
        if not core.valid_items(items):
            self.show_error("Photos should look like 1-10 or 1,3,5-7.")
            return
        out_dir = self.out_dir.get()
        os.makedirs(out_dir, exist_ok=True)
        self.busy(True)
        self.bar["value"] = 0
        total = core.count_items(items) or self.info.count
        args = (self.info_url, out_dir, self.login_browser(), items, total, self.info)
        threading.Thread(target=self._download_photos, args=args, daemon=True).start()

    def _download_photos(self, url, out_dir, browser, items, total, info):
        try:
            files = photos.download(url, out_dir, self.progress, browser, items, total)
            history.add(info.title or f"{info.site} photos", url, files, "photos", info.site)
            self.ui(self._done, core.Result(False, files, []))
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
            messagebox.showwarning("Some extras failed", "\n\n".join(res.warnings[:5]), parent=self)
        self.next_in_queue()


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
