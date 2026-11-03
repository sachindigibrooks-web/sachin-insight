# Free Video & Photo Downloader

**Made by Sachin Samria**

A simple 4K Video Downloader / IDM-style app (desktop app **and** website): paste a video
or playlist link, it lists every available quality — 8K / 4K / 2K / 1080p / 720p …
plus MP3 audio — and downloads with parallel chunks. 100% free, no ads, no limits.
Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

**Sites:** YouTube, Instagram, Facebook, X / Twitter, TikTok, Vimeo, Dailymotion, Reddit,
Twitch, SoundCloud, Pinterest, LinkedIn and [1000+ more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Photo download

Photo wala link daalo (Instagram post, Pinterest pin ya board, X / Twitter, Reddit, Tumblr,
Flickr, Imgur… 300+ sites). Link me video na mile to app apne aap photos dhundh leti hai aur
dikhati hai kitni mili. **Which ones** me `1-10` likh kar kuch hi photos le sakte ho.
Photos original quality me `Save to` ke andar `Photos/<site>` folder me aati hain; website
ek se zyada photo ek `.zip` me deti hai. Instagram photos ke liye aksar login chahiye —
neeche "Private / login wali" dekho. ([gallery-dl](https://github.com/mikf/gallery-dl) se.)

## Playlist download

Playlist ka link daalo (ya playlist wali video ka link daal kar **Download full playlist**
tick karo). Quality "Up to 1080p" jaisi hoti hai — har video us quality tak ki best me aati hai.
**Videos** box me `1-10` ya `1,3,5-7` likh kar sirf kuch videos le sakte ho (khali = saari).
Desktop app playlist ke naam ka folder banati hai; website ek `.zip` file deti hai.
Private / deleted videos apne aap skip ho jaati hain.

## More options (advanced features)

Desktop app me **▸ More options** dabao, website me **More options** kholo.

| Feature | Kya karta hai |
|---|---|
| **Clip only** | Sirf ek hissa download karo, jaise `1:20:00` se `1:35:00`. Poori video download nahi hoti. |
| **Skip sponsors** | YouTube video se sponsor, intro, outro aur "subscribe karo" wale hisse kaat deta hai ([SponsorBlock](https://sponsor.ajay.app) data se). |
| **Data limit** | MB likho (jaise `500`) — app wo best quality chun leti hai jo itne MB me aaye. Clip ke saath bhi hisaab lagata hai. Playlist me ye poori playlist ka total hai. Size andaza hai; jo site size nahi batati (jaise Dailymotion) wahan kaam nahi karta — YouTube par karta hai. |
| **AI subtitles** | Video ke subtitles 24 bhashaon me — Hindi, English, Tamil, Telugu, Bengali, Marathi, Urdu… Pehle site ke apne subtitles dhundhta hai (YouTube Hindi auto-translate bhi deta hai); na mile to **aapke PC par AI** bolne ko sun kar likhta hai (Whisper) aur translate karta hai (NLLB). Internet par kuch upload nahi hota. Teen tarike: video me add (on/off ho sakte hain), video ki picture me hamesha ke liye (burn), ya sirf `.srt` file. |
| **WhatsApp copy** | Video ki ek aur copy jo 16 / 64 / 100 MB me fit ho aur har phone par chale. |
| **Clipboard watcher** (sirf desktop app) | IDM jaisa: kahin bhi video link copy karo, kone me popup aata hai — "Download (best quality)" ya "Choose quality". Download chal raha ho to naye link queue me lag jaate hain. |

**AI subtitles ke baare me:**
- Pehli baar AI models ek baar download hote hain: Fast ≈ 150 MB, Accurate ≈ 460 MB, translation ≈ 630 MB. Uske baad offline chalta hai.
- Speed PC par depend karti hai — normal laptop par "Accurate" 10 minute ki video me lagbhag 5–10 minute leta hai. Jaldi chahiye to "Fast" chuno.
- Translation model (NLLB, Meta) ka license **non-commercial** hai — free tool ke liye theek hai, isse paisa kamane wale product me mat lagana.

## Private / login wali videos (Instagram, Facebook, …)

Kuch videos bina login ke nahi milti (private posts, stories, age-restricted). Unke liye:
1. Apne browser (Firefox sabse achha chalta hai) me us site par login karo.
2. Browser poora band karo.
3. App me **Use login from** me wo browser chuno aur dobara try karo.

App browser ka saved login use karti hai — password kabhi nahi maangti ya save karti.
Chrome/Edge par kabhi-kabhi login read nahi hota; tab Firefox use karo.

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
python core.py "<playlist-url>" 3 D:\Videos --items=1-10  # playlist ki pehli 10 videos
python core.py "<url>" 1 D:\Videos --start=1:20 --end=2:00 --subs=hi --burn --whatsapp=16
```

## Tips

- YouTube kabhi kabhi format badal deta hai; download fail ho to `pip install -U yt-dlp` karo.
- "Sign in to confirm you're not a bot" error aaye to VPN/server IP band karke ghar ke
  internet se try karo.
- Sirf wahi videos download karo jinka aapko haq hai (apni videos, Creative Commons,
  ya permission wali). YouTube ki Terms of Service downloading ko restrict karti hain.
