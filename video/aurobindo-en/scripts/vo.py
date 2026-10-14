"""English narration with Chatterbox TTS (Resemble AI, MIT licence), run in its own Python 3.12 venv.
Line-by-line so each phrase gets its own energy (exaggeration) and pace (cfg_weight: lower = slower, more deliberate).
Two takes per line; pick_takes.py keeps the take whose Whisper transcript matches the script best."""
import json, sys, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# (text, gap after in s, exaggeration, cfg_weight)
LINES = [
    ("Wait. Stop for one second.", 0.45, 0.55, 0.45),
    ("How many thoughts are running through your head right now?", 0.55, 0.6, 0.45),
    ("Now ask yourself...", 0.35, 0.5, 0.3),
    ("who is watching them?", 0.8, 0.35, 0.3),
    ("A freedom fighter, who became a yogi.", 0.35, 0.5, 0.4),
    ("Sri Aurobindo.", 0.4, 0.5, 0.35),
    ("And for him, that one question was the key.", 0.7, 0.55, 0.4),
    ("He saw consciousness as a ladder.", 0.35, 0.5, 0.4),
    ("At the bottom, Matter. Then, Life. Then, Mind...", 0.25, 0.5, 0.35),
    ("which is exactly where we get stuck. Overthinking.", 0.6, 0.6, 0.4),
    ("But Mind is not the last step.", 0.35, 0.55, 0.4),
    ("Above it is the Supermind.", 0.5, 0.7, 0.35),
    ("A consciousness that doesn't think... it simply knows.", 0.6, 0.5, 0.35),
    ("Humans are not the final stage. We are transitional beings.", 0.8, 0.55, 0.4),
    ("In nineteen oh eight, a yogi told him:", 0.35, 0.5, 0.4),
    ("Sit. Don't think. Just watch your mind.", 0.4, 0.45, 0.3),
    ("When thoughts come, throw them out.", 0.5, 0.55, 0.4),
    ("In three days, his mind went completely silent.", 0.9, 0.45, 0.3),
    ("So today, take just one minute, and watch your thoughts.", 0.45, 0.5, 0.4),
    ("Because the one who is watching...", 0.3, 0.5, 0.35),
    ("that's you.", 0.9, 0.45, 0.3),
    ("All life is Yoga.", 0.5, 0.55, 0.35),
    ("Follow for more.", 0.0, 0.5, 0.45),
]

if __name__ == '__main__':
    out = sys.argv[1]
    m = ChatterboxTTS.from_pretrained(device='cpu')
    for i, (txt, gap, ex, cfg) in enumerate(LINES):
        for k in range(2):
            torch.manual_seed(100 * i + k)
            w = m.generate(txt, exaggeration=ex, cfg_weight=cfg, temperature=0.75)
            ta.save(f'{out}/l{i:02d}_t{k}.wav', w, m.sr)
            print(i, k, round(w.shape[-1] / m.sr, 2), txt, flush=True)
    json.dump(LINES, open(f'{out}/lines.json', 'w'))
