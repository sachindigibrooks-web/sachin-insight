"""Hindi / English interface text, shared by the desktop app and the website.

UI holds the fixed labels (by key). PHRASES turns the changing status and
progress messages into Hindi piece by piece, so new messages built from known
phrases are translated too; anything unknown simply stays in English.
"""

UI = {
    "app_title": ("Free Video & Photo Downloader", "फ्री वीडियो और फोटो डाउनलोडर"),
    "credit": ("Made by Sachin Samria", "निर्माता: Sachin Samria"),
    "url": ("Link:", "लिंक:"),
    "fetch": ("Paste & Fetch", "पेस्ट करें और खोजें"),
    "get": ("Get", "खोजें"),
    "url_placeholder": ("Paste a video, playlist or photo link...",
                        "वीडियो, प्लेलिस्ट या फोटो का लिंक पेस्ट करें..."),
    "quality": ("Quality:", "क्वालिटी:"),
    "save_to": ("Save to:", "कहाँ सेव करें:"),
    "browse": ("Browse", "चुनें"),
    "login": ("Use login from:", "लॉगिन यहाँ से लें:"),
    "more_show": ("▸ More options: clip, skip sponsors, data limit, AI subtitles, WhatsApp, "
                  "ringtone, search",
                  "▸ और विकल्प: क्लिप, स्पॉन्सर हटाएँ, डेटा लिमिट, AI सबटाइटल, WhatsApp, "
                  "रिंगटोन, सर्च"),
    "more_hide": ("▾ Hide more options", "▾ विकल्प छिपाएँ"),
    "more_box": ("More options", "और विकल्प"),
    "clip": ("Clip only:", "सिर्फ़ हिस्सा:"),
    "from": ("from", "से"),
    "to": ("to", "तक"),
    "clip_hint": ("e.g. 1:20:00  (empty = full video)", "जैसे 1:20:00  (खाली = पूरी वीडियो)"),
    "sponsor": ("Skip sponsors, intros, outros and 'subscribe' reminders (YouTube)",
                "स्पॉन्सर, इंट्रो, आउट्रो और 'सब्सक्राइब' वाले हिस्से हटाएँ (YouTube)"),
    "limit": ("Data limit:", "डेटा लिमिट:"),
    "limit_hint": ("MB  - picks the best quality that fits (playlist: total size)",
                   "MB  - इतने में आने वाली सबसे अच्छी क्वालिटी (प्लेलिस्ट: कुल साइज़)"),
    "subs": ("Subtitles (AI):", "सबटाइटल (AI):"),
    "whatsapp": ("WhatsApp copy:", "WhatsApp कॉपी:"),
    "ringtone": ("Ringtone (30 sec) from:", "रिंगटोन (30 सेकंड) यहाँ से:"),
    "ringtone_hint": ("e.g. 0:45  (empty = no ringtone)", "जैसे 0:45  (खाली = रिंगटोन नहीं)"),
    "searchable": ("Make it searchable: find words spoken in it later (AI)",
                   "सर्च लायक बनाएँ: इसमें बोले गए शब्द बाद में खोजें (AI)"),
    "download": ("Download", "डाउनलोड"),
    "open_folder": ("Open folder", "फ़ोल्डर खोलें"),
    "watch": ("Watch clipboard (popup when a link is copied)",
              "क्लिपबोर्ड देखें (लिंक कॉपी होते ही पॉपअप)"),
    "whole_playlist": ("Download full playlist", "पूरी प्लेलिस्ट डाउनलोड करें"),
    "items_videos": ("   Videos (e.g. 1-10, blank = all):", "   वीडियो (जैसे 1-10, खाली = सभी):"),
    "items_photos": ("Which ones (e.g. 1-10, blank = all):", "कौन-सी (जैसे 1-10, खाली = सभी):"),
    "history": ("History", "हिस्ट्री"),
    "search_videos": ("Search in videos", "वीडियो में खोजें"),
    "follows": ("Follow channels", "चैनल फ़ॉलो करें"),
    "phone": ("Phone / Website", "फ़ोन / वेबसाइट"),
    "language": ("हिंदी", "English"),  # the button shows the other language
    "updates": ("Check updates", "अपडेट देखें"),
    "start": ("Paste a video, playlist or photo link and click Fetch.",
              "वीडियो, प्लेलिस्ट या फोटो का लिंक पेस्ट करें और खोजें दबाएँ।"),
    "videos_from": ("Videos from", "वीडियो यहाँ से"),
    "photos_from": ("Photos from", "फोटो यहाँ से"),
    "more_sites": ("and more", "और भी"),
    "off": ("Off", "बंद"),
    "none": ("None", "कोई नहीं"),
    "orig_lang": ("Original language", "मूल भाषा"),
    "mode_embed": ("Add to video (can turn on/off)", "वीडियो में जोड़ें (चालू/बंद हो सके)"),
    "mode_burn": ("Burn into the picture", "तस्वीर पर छापें"),
    "mode_srt": ("Only a .srt file", "सिर्फ़ .srt फ़ाइल"),
    "ai_accurate": ("Accurate (slower)", "सटीक (धीमा)"),
    "ai_fast": ("Fast", "तेज़"),
    "search": ("Search", "खोजें"),
    "open": ("Open", "खोलें"),
    "play_here": ("Play from here", "यहाँ से चलाएँ"),
    "again": ("Download again", "फिर से डाउनलोड"),
    "delete": ("Remove", "हटाएँ"),
    "make_searchable": ("Make searchable (AI)", "सर्च लायक बनाएँ (AI)"),
    "check_now": ("Check now", "अभी देखें"),
    "add": ("Add", "जोड़ें"),
    "follow_hint": ("Paste a YouTube channel / playlist or an Instagram / Pinterest profile. "
                    "New uploads download automatically while this app is open (checked every hour).",
                    "YouTube चैनल / प्लेलिस्ट या Instagram / Pinterest प्रोफ़ाइल पेस्ट करें। "
                    "ऐप खुला रहने पर नई वीडियो/फोटो अपने आप डाउनलोड होंगी (हर घंटे चेक)।"),
    "first_time": ("Download now (latest):", "अभी डाउनलोड करें (नई वाली):"),
    "phone_hint": ("Scan with your phone's camera (phone and PC on the same Wi-Fi):",
                   "फ़ोन के कैमरे से स्कैन करें (फ़ोन और PC एक ही Wi-Fi पर हों):"),
    "search_hint": ("Type a word spoken in your downloaded videos (at least 3 letters):",
                    "डाउनलोड की गई वीडियो में बोला गया शब्द लिखें (कम से कम 3 अक्षर):"),
    "private": ("Private or login-only? (Instagram photos & stories, private posts, age-restricted…)",
                "प्राइवेट या लॉगिन वाली? (Instagram फोटो और स्टोरी, प्राइवेट पोस्ट, उम्र-प्रतिबंधित…)"),
    "private_hint": ("Log in to the site in that browser on the PC running this downloader, close "
                     "the browser, then try again. Your password is never seen or stored.",
                     "उस ब्राउज़र में साइट पर लॉगिन करें, ब्राउज़र बंद करें, फिर दोबारा कोशिश करें। "
                     "आपका पासवर्ड कभी देखा या सेव नहीं होता।"),
    "which_ones": ("Which ones", "कौन-सी"),
    "videos_label": ("Videos", "वीडियो"),
    "ai_note": ("AI runs on this PC. The first time, the AI models download once (≈150–1100 MB).",
                "AI इसी PC पर चलता है। पहली बार AI मॉडल एक बार डाउनलोड होते हैं (≈150–1100 MB)।"),
    "disclaimer": ("Only download videos and photos you own or have permission to download.",
                   "सिर्फ़ वही वीडियो और फोटो डाउनलोड करें जिनका आपको अधिकार या अनुमति है।"),
}

LANGUAGE_NAMES_HI = {
    "Hindi": "हिंदी", "English": "अंग्रेज़ी", "Bengali": "बांग्ला", "Marathi": "मराठी",
    "Tamil": "तमिल", "Telugu": "तेलुगु", "Gujarati": "गुजराती", "Kannada": "कन्नड़",
    "Malayalam": "मलयालम", "Punjabi": "पंजाबी", "Urdu": "उर्दू", "Nepali": "नेपाली",
    "Arabic": "अरबी", "Spanish": "स्पेनिश", "French": "फ़्रेंच", "German": "जर्मन",
    "Portuguese": "पुर्तगाली", "Russian": "रूसी", "Japanese": "जापानी", "Korean": "कोरियाई",
    "Chinese": "चीनी", "Indonesian": "इंडोनेशियाई", "Turkish": "तुर्की", "Italian": "इतालवी",
}

PHRASES = [
    ("Download complete!", "डाउनलोड पूरा हुआ!"),
    ("Fetching available qualities...", "क्वालिटी देख रहे हैं..."),
    ("Reading playlist...", "प्लेलिस्ट पढ़ रहे हैं..."),
    ("options found. Highest quality is selected.", "विकल्प मिले। सबसे अच्छी क्वालिटी चुनी गई है।"),
    ("options found — highest quality selected.", "विकल्प मिले — सबसे अच्छी क्वालिटी चुनी गई।"),
    ("Processing (merging audio + video)...", "प्रोसेस हो रहा है (ऑडियो + वीडियो जोड़ रहे हैं)..."),
    ("Writing subtitles with AI", "AI से सबटाइटल लिख रहे हैं"),
    ("Translating subtitles", "सबटाइटल का अनुवाद हो रहा है"),
    ("Listening to the video (AI)...", "AI वीडियो सुन रहा है..."),
    ("Adding subtitles into the video", "वीडियो में सबटाइटल जोड़ रहे हैं"),
    ("Making WhatsApp copy", "WhatsApp कॉपी बना रहे हैं"),
    ("Making ringtone", "रिंगटोन बना रहे हैं"),
    ("Making it searchable (AI)", "सर्च लायक बना रहे हैं (AI)"),
    ("Looking for the site's own subtitles...", "साइट के अपने सबटाइटल खोज रहे हैं..."),
    ("Loading AI translation model - first time downloads ~630 MB, please wait...",
     "AI अनुवाद मॉडल लोड हो रहा है - पहली बार ~630 MB डाउनलोड होगा, कृपया रुकें..."),
    ("Loading AI speech model", "AI स्पीच मॉडल लोड हो रहा है"),
    ("first time downloads it, please wait...", "पहली बार डाउनलोड होगा, कृपया रुकें..."),
    ("Some videos were skipped (private, deleted or blocked).",
     "कुछ वीडियो छोड़ दी गईं (प्राइवेट, डिलीट या ब्लॉक)।"),
    ("Photos are saved in a 'Photos' folder inside Save to.",
     "फोटो 'Photos' फ़ोल्डर में सेव होंगी।"),
    ("This video is part of a playlist - tick the box to download all of it.",
     "यह वीडियो एक प्लेलिस्ट का हिस्सा है - पूरी प्लेलिस्ट के लिए बॉक्स पर टिक करें।"),
    ("Pick a quality; each video downloads at the best quality up to it.",
     "क्वालिटी चुनें; हर वीडियो उस क्वालिटी तक की सबसे अच्छी में आएगी।"),
    ("It starts after the current download.", "यह मौजूदा डाउनलोड के बाद शुरू होगा।"),
    ("Added to queue", "कतार में जोड़ा"),
    ("waiting", "इंतज़ार में"),
    ("Could not read this link:", "यह लिंक नहीं पढ़ पाए:"),
    ("Download failed:", "डाउनलोड नहीं हुआ:"),
    ("This video / post needs a login.", "इस वीडियो / पोस्ट के लिए लॉगिन चाहिए।"),
    ("No photos or videos found at this link.", "इस लिंक पर कोई फोटो या वीडियो नहीं मिली।"),
    ("Starting download on server...", "डाउनलोड शुरू हो रहा है..."),
    ("Ready! Your download is starting...", "तैयार! आपका डाउनलोड शुरू हो रहा है..."),
    ("Packing the files into one .zip file...", "फ़ाइलें एक .zip में डाल रहे हैं..."),
    ("Packing the photos into one .zip file...", "फोटो एक .zip में डाल रहे हैं..."),
    ("Starting...", "शुरू हो रहा है..."),
    ("Ready!", "तैयार!"),
    ("Error.", "गड़बड़ी।"),
    ("Data limit:", "डेटा लिमिट:"),
    ("fits", "फिट है"),
    ("Saved ", "सेव हुईं "),
    (" files", " फ़ाइलें"),
    ("Video ", "वीडियो "),
    ("ETA", "बाकी"),
    ("found", "मिलीं"),
]
PHRASES.sort(key=lambda p: -len(p[0]))  # replace longer phrases before their parts


def ui(key, lang):
    en, hi = UI[key]
    return hi if lang == "hi" else en


def text(message, lang):
    """Translate a status / progress message phrase by phrase."""
    if lang != "hi" or not message:
        return message
    for en, hi in PHRASES:
        message = message.replace(en, hi)
    return message


def language_name(name, lang):
    return LANGUAGE_NAMES_HI.get(name, name) if lang == "hi" else name
