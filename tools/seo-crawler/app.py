"""Desktop launcher: starts the dashboard in the background and opens it in the browser.

The dashboard only listens on this PC (127.0.0.1). Closing this window stops it.
"""

import tkinter as tk
import webbrowser
from tkinter import ttk

import server


def main():
    port = server.serve_background()
    url = f"http://localhost:{port}"
    root = tk.Tk()
    root.title("Free SEO Crawler - Made by Sachin Samria")
    root.resizable(False, False)
    body = ttk.Frame(root, padding=18)
    body.pack()
    ttk.Label(body, text="Free SEO Crawler", font=("", 15, "bold")).pack()
    ttk.Label(body, text="Made by Sachin Samria", foreground="gray").pack(pady=(0, 10))
    ttk.Label(body, text="The dashboard is running in your browser:\n"
                         "डैशबोर्ड आपके ब्राउज़र में चल रहा है:", justify="center").pack()
    link = ttk.Label(body, text=url, foreground="#1a5fb4", cursor="hand2", font=("", 11, "bold"))
    link.pack(pady=6)
    link.bind("<Button-1>", lambda e: webbrowser.open(url))
    ttk.Button(body, text="Open dashboard / डैशबोर्ड खोलें", command=lambda: webbrowser.open(url)).pack(pady=4)
    ttk.Label(body, text="Keep this window open while crawling. Close it to quit.\n"
                         "क्रॉल के दौरान यह विंडो खुली रखें। बंद करने पर ऐप बंद हो जाएगा।",
              foreground="gray", justify="center").pack(pady=(8, 0))
    root.after(600, lambda: webbrowser.open(url))
    root.mainloop()


if __name__ == "__main__":
    main()
