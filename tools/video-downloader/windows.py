"""The desktop app's extra windows: history, search in videos, follows, phone / website."""

import os
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import core
import follows
import history
import i18n
import qr
import searchindex


def open_path(path):
    if os.name == "nt":
        os.startfile(path)
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])


def show_in_folder(path):
    if os.name == "nt":
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    else:
        open_path(os.path.dirname(path))


def clock(seconds):
    s = int(seconds)
    return f"{s // 3600}:{s // 60 % 60:02}:{s % 60:02}" if s >= 3600 else f"{s // 60}:{s % 60:02}"


class Window(tk.Toplevel):
    """A child window that follows the app's language."""

    def __init__(self, app, title_key, size):
        super().__init__(app)
        self.app = app
        self.title(app.t(title_key))
        self.geometry(size)
        self.minsize(520, 300)

    def t(self, key):
        return self.app.t(key)

    def button(self, parent, key, command):
        b = ttk.Button(parent, text=self.t(key), command=command)
        b.pack(side="left", padx=(0, 6))
        return b

    def table(self, columns, widths):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=6)
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col, (name, width) in zip(columns, widths):
            tree.heading(col, text=name)
            tree.column(col, width=width, stretch=col == columns[-1] or width > 200)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree


class HistoryWindow(Window):
    def __init__(self, app):
        super().__init__(app, "history", "820x480")
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=(10, 0))
        self.query = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.query)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<KeyRelease>", lambda e: self.refresh())
        hi = app.lang == "hi"
        self.tree = self.table(("when", "kind", "title"),
                               (("कब" if hi else "When", 150), ("क्या" if hi else "Type", 80),
                                ("नाम" if hi else "Title", 520)))
        self.tree.bind("<Double-1>", lambda e: self.open())
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=(0, 10))
        self.button(btns, "open", self.open)
        self.button(btns, "open_folder", self.folder)
        self.button(btns, "again", self.again)
        self.button(btns, "make_searchable", self.make_searchable)
        self.button(btns, "delete", self.remove)
        self.status = ttk.Label(self, foreground="gray")
        self.status.pack(fill="x", padx=10, pady=(0, 8))
        self.refresh()
        entry.focus_set()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        self.items = {e["id"]: e for e in history.search(self.query.get())}
        for e in self.items.values():
            when = time.strftime("%d %b %Y %H:%M", time.localtime(e["time"]))
            self.tree.insert("", "end", iid=e["id"], values=(when, e["kind"], e["title"]))

    def selected(self):
        sel = self.tree.selection()
        return self.items.get(sel[0]) if sel else None

    def open(self):
        e = self.selected()
        f = e and history.main_file(e)
        if f:
            open_path(f)
        elif e:
            messagebox.showinfo("", "The file was moved or deleted.", parent=self)

    def folder(self):
        e = self.selected()
        f = e and history.main_file(e)
        if f:
            show_in_folder(f)

    def again(self):
        e = self.selected()
        if e:
            self.destroy()
            self.app.url.set(e["url"])
            self.app.fetch()

    def remove(self):
        e = self.selected()
        if e:
            history.remove(e["id"])
            self.refresh()

    def make_searchable(self):
        e = self.selected()
        f = e and history.main_file(e)
        if not f:
            return
        self.status.config(text="AI is listening to the video...")

        def run():
            import extras
            try:
                lines, _ = extras.ai_subtitles(f, extras.ORIGINAL, "fast", lambda p, t: self.after(
                    0, lambda: self.winfo_exists() and self.status.config(text=t)))
                searchindex.add(f, e["title"], lines)
                msg = f"Done - {len(lines)} lines can now be found in '{self.t('search_videos')}'."
            except Exception as err:
                msg = f"Could not do it: {err}"
            self.after(0, lambda: self.winfo_exists() and self.status.config(text=msg))
        threading.Thread(target=run, daemon=True).start()


class SearchWindow(Window):
    def __init__(self, app):
        super().__init__(app, "search_videos", "820x480")
        ttk.Label(self, text=self.t("search_hint")).pack(anchor="w", padx=10, pady=(10, 2))
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10)
        self.query = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.query)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda e: self.search())
        ttk.Button(top, text=self.t("search"), command=self.search).pack(side="left", padx=6)
        hi = app.lang == "hi"
        self.tree = self.table(("at", "title", "text"),
                               (("समय" if hi else "At", 70), ("वीडियो" if hi else "Video", 260),
                                ("बोला गया" if hi else "Spoken", 420)))
        self.tree.bind("<Double-1>", lambda e: self.play())
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=(0, 10))
        self.button(btns, "play_here", self.play)
        self.button(btns, "open_folder", self.folder)
        n = searchindex.count()
        self.note = ttk.Label(btns, foreground="gray", text=(
            f"{n} searchable videos." if n else "No searchable videos yet - tick 'Make it "
            "searchable' in More options, or use History > Make searchable."))
        self.note.pack(side="left", padx=10)
        entry.focus_set()

    def search(self):
        self.tree.delete(*self.tree.get_children())
        self.results = searchindex.search(self.query.get())
        for i, r in enumerate(self.results):
            self.tree.insert("", "end", iid=str(i), values=(clock(r["start"]), r["title"], r["text"]))
        if len(self.query.get().strip()) < 3:
            self.note.config(text="Type at least 3 letters.")
        else:
            self.note.config(text=f"{len(self.results)} found.")

    def selected(self):
        sel = self.tree.selection()
        return self.results[int(sel[0])] if sel else None

    def play(self):
        r = self.selected()
        if r:
            import web
            port = web.serve_background()
            webbrowser.open(f"http://localhost:{port}/watch/{r['video_id']}?t={int(r['start'])}")

    def folder(self):
        r = self.selected()
        if r:
            show_in_folder(r["path"])


class FollowsWindow(Window):
    def __init__(self, app):
        super().__init__(app, "follows", "820x480")
        ttk.Label(self, text=self.t("follow_hint"), wraplength=780, foreground="gray").pack(
            anchor="w", padx=10, pady=(10, 4))
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10)
        self.url = tk.StringVar()
        ttk.Entry(top, textvariable=self.url).pack(side="left", fill="x", expand=True)
        self.quality = ttk.Combobox(top, state="readonly", width=8, values=list(follows.QUALITIES))
        self.quality.set("best")
        self.quality.pack(side="left", padx=6)
        ttk.Label(top, text=self.t("first_time")).pack(side="left")
        self.first_n = ttk.Spinbox(top, from_=0, to=50, width=4)
        self.first_n.set(3)
        self.first_n.pack(side="left", padx=4)
        self.add_btn = ttk.Button(top, text=self.t("add"), command=self.add)
        self.add_btn.pack(side="left")
        hi = app.lang == "hi"
        self.tree = self.table(("site", "kind", "last", "total", "title"), (
            ("साइट" if hi else "Site", 100), ("क्या" if hi else "Type", 70),
            ("आखिरी चेक" if hi else "Last check", 130), ("कुल" if hi else "Got", 60),
            ("नाम" if hi else "Name", 400)))
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=(0, 10))
        self.button(btns, "check_now", self.check_now)
        self.button(btns, "delete", self.remove)
        self.status = ttk.Label(btns, foreground="gray")
        self.status.pack(side="left", padx=10)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for f in follows.entries():
            last = (time.strftime("%d %b %H:%M", time.localtime(f["last_check"]))
                    if f["last_check"] else "-")
            self.tree.insert("", "end", iid=f["id"], values=(
                f["site"], f["kind"], last, f.get("total", 0), f["title"]))

    def say(self, text):
        self.after(0, lambda: self.winfo_exists() and self.status.config(text=text))

    def add(self):
        url = self.url.get().strip()
        if not url.startswith("http"):
            return
        self.add_btn.config(state="disabled")
        self.say("Reading the channel / profile...")
        args = (url, self.app.out_dir.get(), self.quality.get(), int(self.first_n.get() or 0))
        browser = self.app.login_browser()  # read widgets here: Tk isn't thread-safe

        def run():
            try:
                f = follows.add(*args, browser=browser)
                self.say(f"Following '{f['title'][:50]}'. Downloading the latest now...")
                self.after(0, self.refresh)
                files = follows.check(f, self.progress, browser)
                if files:
                    history.add(f["title"], f["url"], files, "follow", f["site"])
                self.say(f"Following '{f['title'][:50]}' - {len(files)} file(s) downloaded. "
                         "New uploads will download automatically.")
            except Exception as e:
                self.say(f"Could not follow: {core.friendly_error(e)}")
            self.after(0, lambda: self.winfo_exists() and (
                self.add_btn.config(state="normal"), self.url.set(""), self.refresh()))
        threading.Thread(target=run, daemon=True).start()

    def progress(self, pct, text):
        self.say(text)

    def selected(self):
        sel = self.tree.selection()
        return next((f for f in follows.entries() if sel and f["id"] == sel[0]), None)

    def check_now(self):
        f = self.selected()
        if not f:
            return
        self.say("Checking...")
        browser = self.app.login_browser()

        def run():
            try:
                files = follows.check(f, self.progress, browser)
                if files:
                    history.add(f["title"], f["url"], files, "follow", f["site"])
                self.say(f"{len(files)} new file(s).")
            except Exception as e:
                self.say(core.friendly_error(e))
            self.after(0, lambda: self.winfo_exists() and self.refresh())
        threading.Thread(target=run, daemon=True).start()

    def remove(self):
        f = self.selected()
        if f:
            follows.remove(f["id"])
            self.refresh()


class PhoneWindow(Window):
    """Starts the website on this PC and shows a QR code for phones on the same Wi-Fi."""

    def __init__(self, app):
        super().__init__(app, "phone", "420x560")
        import web
        port = web.serve_background()
        phone_url = f"http://{qr.lan_ip()}:{port}"
        local_url = f"http://localhost:{port}"
        ttk.Label(self, text=self.t("phone_hint"), wraplength=380).pack(padx=12, pady=(12, 6))
        matrix = qr.matrix(phone_url)
        cell = max(3, 300 // len(matrix))
        canvas = tk.Canvas(self, width=len(matrix) * cell, height=len(matrix) * cell,
                           bg="white", highlightthickness=0)
        for y, row in enumerate(matrix):
            for x, dark in enumerate(row):
                if dark:
                    canvas.create_rectangle(x * cell, y * cell, (x + 1) * cell, (y + 1) * cell,
                                            fill="black", width=0)
        canvas.pack(pady=6)
        ttk.Label(self, text=phone_url, font=("", 12, "bold")).pack(pady=4)
        link = ttk.Label(self, text=local_url, foreground="#1a5fb4", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open(local_url))
        ttk.Label(self, text=i18n.text("Keep this app open while using the website. If the phone "
                                       "can't open it, allow the app in Windows Firewall.",
                                       app.lang),
                  wraplength=380, foreground="gray").pack(padx=12, pady=10)
