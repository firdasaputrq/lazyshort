# 🎬 Anime Shorts Generator - Versi Gratis + GitHub Actions

Generate dan upload YouTube Shorts anime otomatis, **100% gratis**.

## Stack Teknologi

| Komponen | Tools | Biaya |
|---|---|---|
| AI Script | Google Gemini 2.0 Flash | ✅ Gratis |
| Text-to-Speech | edge-tts (Microsoft Edge) | ✅ Gratis |
| Cari Gambar | DuckDuckGo Search | ✅ Gratis |
| Video Render | MoviePy + FFmpeg | ✅ Gratis |
| Otomasi | GitHub Actions | ✅ Gratis (2000 menit/bulan) |
| Upload | YouTube Data API v3 | ✅ Gratis |

---

## Setup Awal (Lakukan Sekali di PC)

### Langkah 1 — Siapkan Gemini API Key

1. Buka [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Login dengan Google
3. Klik **Create API Key**
4. Copy API key-nya, simpan dulu

### Langkah 2 — Siapkan YouTube API

1. Buka [console.cloud.google.com](https://console.cloud.google.com/)
2. Buat project baru (misalnya: `anime-shorts-bot`)
3. Pergi ke **APIs & Services → Library**
4. Cari dan **Enable** → `YouTube Data API v3`
5. Pergi ke **APIs & Services → Credentials**
6. Klik **Create Credentials → OAuth 2.0 Client ID**
7. Application type: **Desktop app**
8. Download JSON → simpan sebagai `client_secret.json` di folder project

### Langkah 3 — Generate YouTube Token

Install dulu dependency yang diperlukan:

```bash
pip install google-auth-oauthlib google-api-python-client
```

Jalankan setup script:

```bash
python setup_youtube_token.py
```

Browser akan terbuka → login ke akun YouTube channel kamu → izinkan akses.

Script akan menampilkan JSON seperti ini:
```json
{"client_id":"xxx","client_secret":"yyy","refresh_token":"zzz"}
```

**Copy teks JSON tersebut** — dibutuhkan di langkah berikutnya.

### Langkah 4 — Tambah GitHub Secrets

Di repository GitHub kamu:
1. Buka **Settings → Secrets and variables → Actions**
2. Klik **New repository secret**

Tambahkan 2 secrets berikut:

| Name | Value |
|---|---|
| `GEMINI_API_KEY` | API key dari Langkah 1 |
| `YOUTUBE_TOKEN_JSON` | JSON dari Langkah 3 |

### Langkah 5 — Push ke GitHub

```bash
git add .
git commit -m "feat: anime shorts generator dengan GitHub Actions"
git push
```

Workflow akan aktif otomatis sesuai jadwal cron.

---

## Menjalankan Manual

Di tab **Actions** GitHub → pilih workflow → klik **Run workflow**.

Ada 2 opsi saat manual run:
- **Skip TTS** — generate video tanpa narasi suara (lebih cepat)
- **Skip upload** — generate video saja, tidak upload ke YouTube

---

## Konfigurasi Jadwal (Cron)

Edit file `.github/workflows/generate_shorts.yml` bagian ini:

```yaml
schedule:
  - cron: "0 1 * * *"   # 08:00 WIB setiap hari
```

Panduan cron (semua waktu UTC, Indonesia WIB = UTC+7):

| Jadwal | Cron Expression |
|---|---|
| Setiap hari jam 08:00 WIB | `0 1 * * *` |
| Setiap hari jam 12:00 WIB | `0 5 * * *` |
| Setiap hari jam 20:00 WIB | `0 13 * * *` |
| Senin, Rabu, Jumat jam 08:00 WIB | `0 1 * * 1,3,5` |
| 3x sehari (08:00, 14:00, 20:00 WIB) | `0 1,7,13 * * *` |

> Generator cron: [crontab.guru](https://crontab.guru/)

---

## Kustomisasi Suara TTS

Tambahkan di GitHub Secrets atau file `.env` lokal:

```env
TTS_VOICE=en-US-GuyNeural
```

Lihat semua pilihan suara:
```bash
edge-tts --list-voices
```

Rekomendasi:
- `en-US-GuyNeural` — Pria Amerika (default, cocok untuk narasi gaming/anime)
- `en-US-AriaNeural` — Wanita Amerika
- `en-GB-RyanNeural` — Pria British (terdengar lebih dramatis)

---

## Kustomisasi Upload YouTube

Edit `src/youtube_uploader.py` untuk mengubah:
- **Title** — format judul video
- **Description** — deskripsi dan hashtag
- **Tags** — tag untuk SEO
- **Privacy** — `"public"`, `"private"`, atau `"unlisted"`

Untuk test awal, ubah privacy ke `"private"` dulu agar tidak langsung publik.

---

## Batasan GitHub Actions

| Resource | Batas (Repo Public) | Estimasi Usage |
|---|---|---|
| Menit/bulan | 2.000 menit | ~15-20 menit/video |
| Storage artifact | 500 MB | Video disimpan 3 hari |
| YouTube API quota | 10.000 unit/hari | Upload = 1.600 unit |

**Estimasi:** bisa generate ~100 video/bulan (gratis).

---

## Troubleshooting

**Error: `GEMINI_API_KEY tidak ditemukan`**
→ Pastikan secret `GEMINI_API_KEY` sudah ditambahkan di GitHub repo.

**Error: `YOUTUBE_TOKEN_JSON tidak ditemukan`**
→ Jalankan ulang `python setup_youtube_token.py` dan update secret.

**Error: ImageMagick policy**
→ Sudah di-handle otomatis di workflow. Jika masih error, coba `--no-audio`.

**Video tidak muncul di YouTube**
→ Cek tab **Actions** di GitHub untuk melihat log lengkap.
