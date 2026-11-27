"""Generate all 43 MyHeritage voice lines with piper-tts (Piper id_ID-news_tts-medium).

Single-speaker voice; characters differentiated by length_scale:
  narrator (n) 1.00, Dimas (d) 1.05, Ibu (i) 0.95, Rani (r) 1.05.
Writes one trimmed 16-bit mono WAV per line into audio/<id>.wav and
records measured durations in audio/lines.json.
"""
import json, os, wave
import numpy as np
from piper import PiperVoice
from piper.config import SynthesisConfig

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.expanduser("~/models/vits-piper-id_ID-news_tts-medium")
ONNX = os.path.join(MODEL_DIR, "id_ID-news_tts-medium.onnx")
CFG = os.path.join(MODEL_DIR, "id_ID-news_tts-medium.onnx.json")
LINES = json.load(open(os.path.join(BASE, "lines-id.json")))
AUDIO = os.path.join(BASE, "audio")
os.makedirs(AUDIO, exist_ok=True)

LENGTH_SCALE = {"n": 1.0, "d": 1.05, "i": 0.95, "r": 1.05}

def trim(s, sr):
    """Trim leading/trailing silence like the aivxer example (0.012*max threshold)."""
    if len(s) == 0:
        return s
    thr = 0.012 * np.abs(s).max()
    idx = np.where(np.abs(s) > thr)[0]
    if len(idx) == 0:
        return s
    lead = int(0.014 * sr)   # ~300 samples at 22050
    tail = int(0.068 * sr)   # ~1500 samples at 22050
    return s[max(idx[0] - lead, 0): idx[-1] + tail + 1]

def main():
    voice = PiperVoice.load(ONNX, config_path=CFG)
    sr = voice.config.sample_rate
    print("sample rate:", sr)
    out = {}
    total = 0.0
    for line in LINES:
        lid, spk, text = line["id"], line["speaker"], line["text"]
        cfg = SynthesisConfig(length_scale=LENGTH_SCALE[spk])
        chunks = [c.audio_float_array for c in voice.synthesize(text, syn_config=cfg)]
        s = np.concatenate(chunks).astype(np.float32) if chunks else np.zeros(0, np.float32)
        s = trim(s, sr)
        dur = len(s) / sr
        total += dur
        # 16-bit mono WAV via wave module
        pcm = np.clip(s, -1.0, 1.0)
        pcm16 = (pcm * 32767).astype(np.int16)
        path = os.path.join(AUDIO, f"{lid}.wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm16.tobytes())
        out[lid] = {"speaker": spk, "text": text, "dur": round(dur, 3), "sr": sr}
        print(lid, spk, round(dur, 2), text, flush=True)
    json.dump(out, open(os.path.join(AUDIO, "lines.json"), "w"), indent=1, ensure_ascii=False)
    print("TOTAL voice duration:", round(total, 2), "s over", len(out), "lines")

if __name__ == "__main__":
    main()
