# Free Video Downloader

A simple 4K Video Downloader / IDM-style app (desktop app **and** website): paste a YouTube (or 1000+ other
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

## Website version

Browser me chalne wala version — PC, phone, tablet sab par.

```bash
pip install -r requirements.txt
python web.py
```

Phir browser me <http://localhost:8000> kholo (Windows par `start_website.bat` double-click bhi kar sakte ho).

**Phone / ghar ke doosre devices se:** jo PC par `web.py` chal raha hai uska IP nikalo
(`ipconfig` → IPv4 Address, jaise `192.168.1.5`) aur phone ke browser me
`http://192.168.1.5:8000` kholo. Windows Firewall puche to "Allow" karo.

Video pehle server (aapke PC) par download hoti hai, phir browser me save hoti hai.
Settings (environment variables): `PORT` (default 8000), `MAX_PARALLEL` (ek saath kitne
downloads, default 3).

> **Internet par public website banana ho to:** YouTube cloud/VPS server (AWS, Render,
> Railway, DigitalOcean…) ke IP ko block karta hai ("Sign in to confirm you're not a bot").
> Isliye ye ghar ke PC/internet par sabse achha chalta hai. Bahar se access chahiye to
> apne PC par chala kar Cloudflare Tunnel (free) se link share kar sakte ho.

## .exe banana (dusron ko dene ke liye)

`build_windows.bat` par double-click karo (5–10 minute lagte hain). `dist` folder me do files banengi:

- `FreeVideoDownloader.exe` — desktop app
- `FreeVideoDownloaderWeb.exe` — website version; double-click karte hi browser me khulti hai

Ye single files kisi bhi Windows PC par bina Python ke chalengi (ffmpeg andar hi hai).
Pehli baar chalane par Windows "Windows protected your PC" dikha sakta hai (exe signed nahi
hai) — **More info → Run anyway** dabao.

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
