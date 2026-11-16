# Drama Bot Kit

Bot Telegram untuk pencinta drama: cari judul, ikuti drama favorit, dan terima notifikasi otomatis saat episode baru tayang.

> **Jenis proyek:** Toolkit Freelance

## Ringkasan

Drama Bot Kit adalah template bot Telegram siap pakai untuk order freelance, dengan data drama yang diambil dari TVMaze API — endpoint publik gratis tanpa API key, sehingga tidak diperlukan scraping manual. Pengguna mencari judul lewat `/cari`, mengikuti drama dengan `/ikuti`, lalu menerima notifikasi episode baru secara otomatis. Seluruh logika bot ditulis dengan python-telegram-bot dan dilindungi unit test pytest yang berjalan tanpa koneksi jaringan.

## Fitur

- Pencarian drama melalui TVMaze dengan batas lima hasil per kueri, lengkap dengan ID untuk dipakai perintah lain (`bot/tvmaze.py: search_shows`).
- Lima perintah bot: `/cari`, `/detail`, `/ikuti`, `/list`, dan `/berhenti` untuk mencari drama serta mengelola watchlist (`bot/main.py`).
- Deteksi episode baru otomatis lewat job queue `run_repeating` dengan interval default 6 jam yang diatur melalui `CHECK_INTERVAL_HOURS` (`bot/main.py: build_application`).
- Baseline `last_airdate` per drama sehingga episode lama yang sudah tayang tidak ikut dikirim (`bot/store.py: WatchlistStore.set_last_airdate`).
- Watchlist per pengguna disimpan sebagai satu file JSON per chat di folder `data/`, ditulis atomik melalui file `.tmp` lalu rename (`bot/store.py: WatchlistStore.save`).
- Sinopsis dari API dibersihkan dari tag HTML dan dipotong 400 karakter sebelum dikirim ke pengguna (`bot/tvmaze.py: _strip_html`).
- Demo offline `demo.py` memakai data dummy, plus mode `--live` untuk menguji API TVMaze sungguhan.

## Teknologi

![Python](https://img.shields.io/badge/Python-3776AB-3776AB?style=for-the-badge&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4-26A5E4?style=for-the-badge&logo=telegram)
![Requests](https://img.shields.io/badge/Requests-2C6E49-2C6E49?style=for-the-badge)
![pytest](https://img.shields.io/badge/pytest-0A9EDC-0A9EDC?style=for-the-badge&logo=pytest)

## Cara Menjalankan

```powershell
# 1. Virtualenv dan instalasi dependensi
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Konfigurasi
Copy-Item .env.example .env
# Isi BOT_TOKEN dari @BotFather, opsional isi ADMIN_IDS

# 3. Jalankan bot
python -m bot
```

Pengujian dan demo:

```powershell
pytest                # unit test tanpa network
python demo.py        # demo offline dengan data dummy
python demo.py --live # demo memakai API TVMaze asli (butuh internet)
```

## Struktur Proyek

```
drama-bot-kit/
├── bot/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py      # registrasi handler dan job queue
│   ├── store.py     # watchlist per chat (JSON)
│   └── tvmaze.py    # klien TVMaze API
├── tests/
│   ├── test_store.py
│   └── test_tvmaze.py
├── .env.example
├── demo.py
├── pytest.ini
└── requirements.txt
```

## Catatan

- `bot/main.py` memuat variabel lingkungan lewat `python-dotenv`; paket ini belum tercantum di `requirements.txt`, jadi pasang manual dengan `pip install python-dotenv` bila bot gagal start.
- Folder `data/` dibuat otomatis saat bot berjalan dan sudah masuk `.gitignore`.
- Token bot hanya disimpan di `.env`. Jangan pernah melakukan commit file tersebut.

## Lisensi

MIT License — lihat [LICENSE](LICENSE)
