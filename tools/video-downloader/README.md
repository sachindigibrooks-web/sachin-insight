# Free Video Downloader

A simple 4K Video Downloader / IDM-style app: paste a YouTube (or 1000+ other
sites) link, it lists every available quality — 8K / 4K / 2K / 1080p / 720p …
plus MP3 audio — and downloads with parallel chunks. 100% free, no ads, no limits.
Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Chalane ka tarika (Windows)

1. Python 3.10+ install karo: <https://www.python.org/downloads/> (install ke time
   **"Add Python to PATH"** tick karna).
2. Is folder me terminal kholo aur:

   ```bash
   pip install -r requirements.txt
   python app.py
   ```

3. URL paste karo → **Paste & Fetch** → quality chuno → **Download**.

ffmpeg `imageio-ffmpeg` ke saath apne aap aa jata hai (1080p+ video merge aur MP3 ke liye zaroori).

## .exe banana (dusron ko dene ke liye)

`build_windows.bat` par double-click karo. `dist\FreeVideoDownloader.exe` ban jayegi —
ye single file kisi bhi Windows PC par bina Python ke chalegi.

## Command line

```bash
python core.py "<url>"            # qualities list karo
python core.py "<url>" 1 D:\Videos  # option 1 (highest) download karo
```

## Tips

- YouTube kabhi kabhi format badal deta hai; download fail ho to `pip install -U yt-dlp` karo.
- "Sign in to confirm you're not a bot" error aaye to VPN/server IP band karke ghar ke
  internet se try karo.
- Sirf wahi videos download karo jinka aapko haq hai (apni videos, Creative Commons,
  ya permission wali). YouTube ki Terms of Service downloading ko restrict karti hain.
