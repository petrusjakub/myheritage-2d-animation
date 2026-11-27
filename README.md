# MyHeritage — Video Explainer Animasi 2D (Bahasa Indonesia)

Video explainer animasi 2D gaya "money stories drawn on paper" tentang
MyHeritage: email misterius jam 2 pagi, tes DNA, arsip 19,9 miliar catatan,
Smart Matches, sampai dari ruang tamu ke dunia. Durasi ±2:57 (17 shot,
43 baris suara, 152 detik voice + jeda).

Dibuat dengan skill **"Claude 2D Animation Long Form" — Made by aivxer**
(semua gambar digambar via kode skia-python, tanpa aset berhak cipta;
MyHeritage hanya muncul sebagai teks di dalam cerita, bukan logo).
Suara: **Piper TTS `id_ID-news_tts-medium`** (Bahasa Indonesia, satu speaker;
karakter dibedakan lewat `length_scale`: narator 1.0, Dimas 1.05, Ibu 0.95,
Rani 1.05). Musik & SFX disintesis dari kode (numpy/scipy).

## Cara render (GitHub Actions)

1. Buka tab **Actions** di repo ini → workflow **Render MyHeritage**.
2. Klik **Run workflow** → **Run workflow**.
3. Tunggu sampai job selesai (±1 jam; timeout 240 menit).
4. Unduh artifact **`myheritage-final`** (retensi 7 hari) — berisi
   `myheritage-final.mp4` (1920×1080, 30 fps, audio -14 LUFS).

## Isi repo

| File | Fungsi |
|---|---|
| `script-id.md` | Naskah final Bahasa Indonesia (43 baris) + fakta terverifikasi |
| `lines-id.json` | Naskah dalam bentuk machine-readable `{id, speaker, text}` |
| `gen_voices.py` | Generate 43 WAV dengan piper-tts → `audio/<id>.wav` |
| `timeline.py` | Cue & durasi shot dari durasi voice terukur |
| `kit.py` | Drawing kit: karakter puppet orisinal, lighting malam, teks |
| `scenes.py` | Fungsi gambar per shot |
| `render.py` | Render per-shot MP4 (`render.py all` / `render.py 0 5` / `render.py frames 0:0.5`) |
| `audio_mix.py` | Voice chain + musik + SFX + ducking + loudnorm -14 LUFS |
| `join.sh` | Gabung shot (concat demuxer) + mux audio → `myheritage-final.mp4` |
| `run_all.sh` | Pipeline lengkap: voices → render → mix → join |
| `requirements.txt` | Dependensi Python runner |
| `.github/workflows/render-myheritage.yml` | Workflow GitHub Actions |

## Catatan

- **Suara di-generate di runner** (dari `lines-id.json` + model Piper yang
  diunduh saat workflow jalan). Tidak ada file WAV/MP4 biner di repo ini.
- Verifikasi suara dilakukan lokal dengan Whisper ASR (base + small):
  hampir semua baris tertranskripsi benar. Pengecualian: nama merek
  "MyHeritage" selalu salah dengar oleh Whisper (artefak proper-noun, wajar),
  dan kata **"DNA"** (baris n19) secara konsisten ditranskripsikan sebagai
  "dia enak" oleh semua model ASR — dengarkan sekali sebelum publish.
- Fakta di naskah sudah diverifikasi (didirikan 2003 oleh Gilad Japhet,
  tes DNA 2016, 19,9 miliar catatan, akuisisi $600 juta tahun 2021,
  42 bahasa). Harga tes DNA / paket langganan sengaja tidak dikutip.
- Tonton sekali hasil akhirnya untuk memeriksa timing — Claude tidak bisa
  mendengar/menonton playback.
