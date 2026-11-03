"""After-download extras: AI subtitles (with translation), and WhatsApp-sized copies.

Subtitles come from the site when it has them in the wanted language (fast),
otherwise they are made on this computer: Whisper turns speech into text and
NLLB translates it. Both models run offline and are downloaded once on first use.
Heavy libraries are imported only when a feature is used, so the apps start fast.
"""

import os
import re
import shutil
import subprocess
import sys

# Windowed .exe builds have no console; progress bars writing to it would crash.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

# Subtitle languages offered: (name, Whisper/site code, NLLB code).
LANGUAGES = [
    ("Hindi", "hi", "hin_Deva"), ("English", "en", "eng_Latn"), ("Bengali", "bn", "ben_Beng"),
    ("Marathi", "mr", "mar_Deva"), ("Tamil", "ta", "tam_Taml"), ("Telugu", "te", "tel_Telu"),
    ("Gujarati", "gu", "guj_Gujr"), ("Kannada", "kn", "kan_Knda"), ("Malayalam", "ml", "mal_Mlym"),
    ("Punjabi", "pa", "pan_Guru"), ("Urdu", "ur", "urd_Arab"), ("Nepali", "ne", "npi_Deva"),
    ("Arabic", "ar", "arb_Arab"), ("Spanish", "es", "spa_Latn"), ("French", "fr", "fra_Latn"),
    ("German", "de", "deu_Latn"), ("Portuguese", "pt", "por_Latn"), ("Russian", "ru", "rus_Cyrl"),
    ("Japanese", "ja", "jpn_Jpan"), ("Korean", "ko", "kor_Hang"), ("Chinese", "zh", "zho_Hans"),
    ("Indonesian", "id", "ind_Latn"), ("Turkish", "tr", "tur_Latn"), ("Italian", "it", "ita_Latn"),
]
ORIGINAL = "orig"  # subtitles in the language that is spoken, no translation
# Spoken languages Whisper may detect that are not in the menu above.
EXTRA_SOURCES = {"vi": "vie_Latn", "th": "tha_Thai", "fa": "pes_Arab", "nl": "nld_Latn",
                 "pl": "pol_Latn", "uk": "ukr_Cyrl", "ms": "zsm_Latn", "sv": "swe_Latn",
                 "el": "ell_Grek", "he": "heb_Hebr", "ro": "ron_Latn", "cs": "ces_Latn",
                 "hu": "hun_Latn", "fi": "fin_Latn", "da": "dan_Latn", "no": "nob_Latn",
                 "si": "sin_Sinh", "tl": "tgl_Latn", "sw": "swh_Latn"}
NLLB = {code: nllb for _, code, nllb in LANGUAGES} | EXTRA_SOURCES

AI_MODELS = {"accurate": "small", "fast": "base"}  # ~460 MB / ~140 MB downloads
NLLB_REPO = "JustFrederik/nllb-200-distilled-600M-ct2-int8"  # ~630 MB download
WHATSAPP_SIZES = [16, 64, 100]  # MB

NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # don't flash console windows


class ExtrasError(Exception):
    pass


def ffmpeg():
    import core
    exe = core.ffmpeg_location()
    if not exe:
        raise ExtrasError("ffmpeg not found.")
    return exe


def run_ffmpeg(args, duration=None, progress=None, label=""):
    """Run ffmpeg, reporting percent done from its -progress output."""
    cmd = [ffmpeg(), "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
           "-progress", "pipe:1"] + args
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
    for line in proc.stdout:
        if progress and duration and line.startswith("out_time_us="):
            try:
                pct = min(99.0, int(line.split("=")[1]) / 1e6 * 100 / duration)
                progress(pct, f"{label} {pct:.0f}%")
            except ValueError:
                pass
    err = proc.stderr.read()
    if proc.wait():
        raise ExtrasError(f"ffmpeg failed: {err.strip()[-300:]}")


def media_duration(path):
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", path], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", creationflags=NO_WINDOW).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", out)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else None


def has_video(path):
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", path], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", creationflags=NO_WINDOW).stderr
    return bool(re.search(r"Stream #.*Video:", out)) and not re.search(r"Video: (mjpeg|png)", out)


def is_h264(path):
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", path], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", creationflags=NO_WINDOW).stderr
    return "Video: h264" in out


# ---------------------------------------------------------------- subtitles

def site_subtitles(url, lang, base, browser=None):
    """Download the site's own subtitles (YouTube can auto-translate) as base.<lang>.srt."""
    import core
    import yt_dlp
    opts = core.base_opts(browser) | {
        "skip_download": True, "noplaylist": True,
        "writesubtitles": True, "writeautomaticsub": True,
        "subtitleslangs": [lang, f"{lang}-.*"], "subtitlesformat": "srt/vtt/best",
        "outtmpl": base + ".%(ext)s",
        "postprocessors": [{"key": "FFmpegSubtitlesConvertor", "format": "srt"}],
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception:
        return None  # e.g. rate-limited; fall back to AI
    folder, name = os.path.split(base)
    for f in sorted(os.listdir(folder or ".")):
        if f.startswith(name + ".") and f.endswith(".srt"):
            return os.path.join(folder, f)
    return None


def load_audio(path):
    """Decode any media file to 16 kHz mono float32 samples, as Whisper expects."""
    import numpy as np
    raw = subprocess.run([ffmpeg(), "-nostdin", "-loglevel", "error", "-i", path, "-vn",
                          "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True, creationflags=NO_WINDOW).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


_whisper = {}
_nllb = []


def whisper_model(size, progress):
    if size not in _whisper:
        progress(0, f"Loading AI speech model ({size}) - first time downloads it, please wait...")
        from faster_whisper import WhisperModel
        _whisper[size] = WhisperModel(size, device="cpu", compute_type="int8")
    return _whisper[size]


def translator(progress):
    if not _nllb:
        progress(0, "Loading AI translation model - first time downloads ~630 MB, please wait...")
        import ctranslate2
        import sentencepiece
        from huggingface_hub import snapshot_download
        d = snapshot_download(NLLB_REPO, allow_patterns=[
            "config.json", "model.bin", "sentencepiece.bpe.model", "shared_vocabulary.txt"])
        _nllb.append((ctranslate2.Translator(d, device="cpu", compute_type="int8"),
                      sentencepiece.SentencePieceProcessor(
                          model_file=os.path.join(d, "sentencepiece.bpe.model"))))
    return _nllb[0]


def translate(texts, src, tgt, progress):
    model, sp = translator(progress)
    out = []
    for i in range(0, len(texts), 16):
        batch = texts[i:i + 16]
        tokens = [[src] + sp.encode(t, out_type=str) + ["</s>"] for t in batch]
        res = model.translate_batch(tokens, target_prefix=[[tgt]] * len(batch), beam_size=2,
                                    max_decoding_length=256)
        out += [sp.decode(r.hypotheses[0][1:]) for r in res]
        pct = min(100, (i + len(batch)) * 100 / len(texts))
        progress(pct, f"Translating subtitles {pct:.0f}%")
    return out


def ai_subtitles(path, lang, model, progress):
    """Make subtitles with Whisper (+ NLLB translation). Returns [(start, end, text)], lang."""
    audio = load_audio(path)
    duration = len(audio) / 16000 or 1
    wm = whisper_model(AI_MODELS.get(model, "small"), progress)
    progress(0, "Listening to the video (AI)...")
    segments, info = wm.transcribe(audio, vad_filter=True)
    spoken = info.language
    if lang == "en" and spoken != "en":
        # Whisper translates speech straight into English better than text translation.
        segments, info = wm.transcribe(audio, vad_filter=True, task="translate")
    lines = []
    for s in segments:
        lines.append((s.start, s.end, s.text.strip()))
        pct = min(100, s.end * 100 / duration)
        progress(pct, f"Writing subtitles with AI {pct:.0f}%")
    if lang not in (ORIGINAL, spoken, "en") and lines:
        if spoken not in NLLB:
            raise ExtrasError(f"Can't translate from the spoken language ({spoken}).")
        texts = translate([t for _, _, t in lines], NLLB[spoken], NLLB[lang], progress)
        lines = [(a, b, t) for (a, b, _), t in zip(lines, texts)]
    return lines, (spoken if lang == ORIGINAL else lang)


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def write_srt(lines, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, text) in enumerate(lines, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n\n")


def filter_path(p):
    """Escape a path for use inside an ffmpeg filter argument."""
    p = os.path.abspath(p).replace("\\", "/")
    return "'" + p.replace(":", "\\:").replace("'", "\\'") + "'"


INDIC = {"hi", "mr", "ne", "bn", "ta", "te", "gu", "kn", "ml", "pa"}


def font_style(lang):
    """libass needs a font that has the script; pick one the OS ships."""
    if sys.platform == "win32":
        fonts = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        name = "Nirmala UI" if lang in INDIC else "Segoe UI"
    elif sys.platform == "darwin":
        fonts = "/System/Library/Fonts"
        name = "Kohinoor Devanagari" if lang in {"hi", "mr", "ne"} else "Helvetica"
    else:
        fonts = "/usr/share/fonts"
        name = "Noto Sans Devanagari" if lang in {"hi", "mr", "ne"} else "Noto Sans"
    # Text on a see-through dark box: readable on any picture, even at 288p where a
    # thick outline smudges Indic letters together.
    return fonts, (f"FontName={name},FontSize=18,BorderStyle=3,Outline=1,Shadow=0,"
                   "OutlineColour=&H60000000,MarginV=20")


def iso639_2(lang):
    """MP4 keeps only 3-letter language tags; NLLB codes start with (nearly) those."""
    code = NLLB.get(lang, "und")[:3]
    return {"arb": "ara", "pes": "fas", "npi": "nep", "zsm": "msa", "swh": "swa"}.get(code, code)


def add_subtitles(video, srt, lang, mode, duration, progress):
    """mode 'embed': switchable subtitle track (fast). mode 'burn': drawn into the picture."""
    tmp = video + ".tmp" + os.path.splitext(video)[1]
    if mode == "burn":
        fonts, style = font_style(lang)
        vf = f"subtitles={filter_path(srt)}:fontsdir={filter_path(fonts)}:force_style='{style}'"
        run_ffmpeg(["-i", video, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-c:a", "copy", tmp], duration, progress,
                   "Adding subtitles into the video")
    else:
        codec = "srt" if video.endswith(".mkv") else "mov_text"
        run_ffmpeg(["-i", video, "-i", srt, "-map", "0", "-map", "1", "-c", "copy",
                    "-c:s", codec, "-metadata:s:s:0", f"language={iso639_2(lang)}", tmp])
    os.replace(tmp, video)


# ---------------------------------------------------------------- WhatsApp

def whatsapp_copy(video, limit_mb, duration, progress):
    """Re-encode to an H.264 MP4 that fits in `limit_mb` (plays everywhere, incl. WhatsApp)."""
    duration = duration or media_duration(video)
    if not duration:
        raise ExtrasError("Can't read the video length.")
    out = os.path.splitext(video)[0] + f" (WhatsApp {limit_mb}MB).mp4"
    size = os.path.getsize(video)
    if size <= limit_mb * 1024 * 1024 and video.endswith(".mp4") and is_h264(video):
        shutil.copyfile(video, out)  # already fits and plays on phones
        return out
    audio_k = 64 if limit_mb <= 16 else 96
    source_k = size * 8 / 1024 / duration  # never spend more bits than the original has
    for factor in (0.92, 0.80):  # retry smaller if the first try overshoots
        video_k = int(min(limit_mb * 8 * 1024 * factor / duration, source_k) - audio_k)
        if video_k < 80:
            raise ExtrasError(f"Video is too long to fit in {limit_mb} MB. Try a bigger size "
                              f"or clip a part of it.")
        height = 720 if video_k >= 1200 else 480 if video_k >= 400 else 360
        run_ffmpeg(["-i", video, "-vf", f"scale=-2:'min({height},ih)'", "-c:v", "libx264",
                    "-preset", "veryfast", "-b:v", f"{video_k}k", "-maxrate", f"{video_k}k",
                    "-bufsize", f"{video_k * 2}k", "-c:a", "aac", "-b:a", f"{audio_k}k",
                    "-movflags", "+faststart", "-pix_fmt", "yuv420p", out],
                   duration, progress, f"Making WhatsApp copy ({limit_mb} MB)")
        if os.path.getsize(out) <= limit_mb * 1024 * 1024:
            return out
    return out


# ---------------------------------------------------------------- pipeline

def process(files, x, progress, browser=None):
    """Run the chosen extras on each downloaded (path, info) pair.

    Returns a list of warnings (one bad file shouldn't lose the others).
    """
    warnings = []
    for n, (path, info) in enumerate(files, 1):
        tag = f"Video {n}/{len(files)}: " if len(files) > 1 else ""

        def step(pct, text):
            progress(pct, tag + text)

        try:
            # The file's own length: a clip or SponsorBlock cut is shorter than the video.
            duration = media_duration(path) or info.get("duration")
            if x.subs_lang:
                base = os.path.splitext(path)[0]
                srt = None
                if x.subs_lang != ORIGINAL and info.get("webpage_url"):
                    step(0, "Looking for the site's own subtitles...")
                    srt = site_subtitles(info["webpage_url"], x.subs_lang, base, browser)
                    lang = x.subs_lang
                if not srt:
                    lines, lang = ai_subtitles(path, x.subs_lang, x.ai_model, step)
                    if not lines:
                        raise ExtrasError("No speech found for subtitles.")
                    srt = f"{base}.{lang}.srt"
                    write_srt(lines, srt)
                if x.subs_mode != "srt" and has_video(path):
                    add_subtitles(path, srt, lang, x.subs_mode, duration, step)
            if x.whatsapp_mb and has_video(path):
                whatsapp_copy(path, x.whatsapp_mb, duration, step)
        except Exception as e:
            warnings.append(f"{os.path.basename(path)}: {e}")
    return warnings
