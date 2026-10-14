# Builds src/timeline.json: Roman-Hinglish caption words aligned to Whisper timings,
# scene boundaries, and SFX cues. Both the Remotion visuals and the audio mixer read it,
# so every hit lands on the same frame as the graphic it belongs to.
import json
raw = json.load(open("scripts/words_raw.json"))
roman = """Ek|baat|batao...|aakhri|baar|Google|pe|kuch|search|kiya|tha,|toh|kisi|website|pe|click|kiya|tha?|Nahi|na?|Haan,|mujhe|bhi|yaad|nahi.|Kyunki|ab|Google|khud|hi|answer|de|deta|hai.|AI|Mode,|AI|Overview...|aur|ab|toh|Hindi|mein|bhi.|Matlab|aapki|website|number|one|pe|rank|kar|rahi|hai...|phir|bhi|click|ZERO.|Toh|bhai,|2026|_|_|mein|SEO|ka|game|badal|gaya|hai.|Ab|sirf|rank|karna|kaafi|nahi|hai...|AI|ke|answer|mein|aapka|naam|aana|chahiye.|Cite|hona|chahiye.|Ab|ye|hoga|kaise?|Teen|simple|cheezein.|Ek|har|page|pe|seedha|sawaal,|seedha|jawaab.|Jaise|log|bolte|hain,|waise|likho.|Do|apna|naam|har|jagah|hona|chahiye...|YouTube,|Instagram,|Google|Business|Profile|AI|wahin|se|padhta|hai.|Aur|teen|real|data,|real|experience.|Copy-paste|_|wala|content?|AI|seedha|ignore|kar|deta|hai.|Next|episode|mein|bataunga...|Instagram|ab|khud|ek|search|engine|ban|chuka|hai|aur|zyaadatar|_|log|ye|miss|kar|rahe|hain.|Follow|kar|lo,|warna|miss|ho|jayega.""".split("|")
assert len(roman) == len(raw), (len(roman), len(raw))
words = []
for r, w in zip(roman, raw):
    if r == "_":
        words[-1]["e"] = w["e"]
        continue
    words.append({"t": r, "s": w["s"], "e": w["e"]})

def at(token, nth=1):
    """Start time of the nth caption word equal to token (punctuation-insensitive)."""
    c = 0
    for w in words:
        if w["t"].strip(".,?!").lower() == token.lower():
            c += 1
            if c == nth:
                return w["s"]
    raise KeyError(token)

DUR = 70.6
scenes = [
    ("hook",      0.0),
    ("nahi",      at("Nahi")),
    ("ai",        at("Kyunki")),
    ("zero",      at("Matlab")),
    ("gamechange",at("Toh", 3)),
    ("cite",      at("Ab", 3)),
    ("teen",      at("Ab", 4)),
    ("one",       at("Ek", 2)),
    ("two",       at("Do")),
    ("three",     at("Aur", 2)),
    ("cta",       at("Next")),
]
scene_list = []
for i, (name, s) in enumerate(scenes):
    e = scenes[i + 1][1] if i + 1 < len(scenes) else DUR
    scene_list.append({"id": name, "s": round(max(0, s - 0.12), 2), "e": round(e - 0.12, 2) if i + 1 < len(scenes) else DUR})

# Named beats the visuals animate on (and the mixer drops SFX on).
beats = {
    "typeStart": at("search") - 0.05,
    "clickWord": at("click"),
    "nahiNa": at("Nahi"),
    "haan": at("Haan"),
    "answer": at("answer"),
    "aiMode": at("Mode"),
    "aiOverview": at("Overview"),
    "hindi": at("Hindi"),
    "rank1": at("number"),
    "click2": at("click", 2),
    "zero": at("ZERO"),
    "year": at("2026"),
    "seo": at("SEO"),
    "badal": at("badal"),
    "rankStrike": at("rank", 2),
    "kaafiNahi": at("kaafi"),
    "aiCard": at("AI", 3),
    "naam": at("naam"),
    "cite": at("Cite"),
    "kaise": at("kaise"),
    "teen": at("Teen"),
    "simple": at("simple"),
    "n1": at("Ek", 2),
    "sawaal": at("sawaal"),
    "jawaab": at("jawaab"),
    "bolte": at("bolte"),
    "likho": at("likho"),
    "n2": at("Do"),
    "har": at("har", 2),
    "yt": at("YouTube"),
    "ig": at("Instagram"),
    "gbp": at("Google", 3),
    "wahin": at("wahin"),
    "n3": at("teen", 2),
    "realData": at("real"),
    "realExp": at("real", 2),
    "copy": at("Copy-paste"),
    "ignore": at("ignore"),
    "next": at("Next"),
    "insta2": at("Instagram", 2),
    "engine": at("search", 2),
    "zyaada": at("zyaadatar"),
    "follow": at("Follow"),
    "warna": at("warna"),
    "end": words[-1]["e"],
}
beats = {k: round(v, 3) for k, v in beats.items()}

# Caption pages: 1-3 words, break on punctuation or gaps, like the small captions in the reference.
pages, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    gap = (nxt["s"] - w["e"]) if nxt else 9
    if len(cur) >= 3 or w["t"][-1] in ".,?" or gap > 0.35 or nxt is None:
        pages.append({"s": cur[0]["s"], "e": round(min(w["e"] + 0.25, nxt["s"]) if nxt else w["e"] + 0.6, 2), "words": cur})
        cur = []

json.dump({"duration": DUR, "words": words, "pages": pages, "scenes": scene_list, "beats": beats},
          open("src/timeline.json", "w"), ensure_ascii=False, indent=1)
for s in scene_list: print(s)
print(len(words), "words", len(pages), "pages")
