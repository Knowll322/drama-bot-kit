# Drama Bot Kit

Bot Telegram untuk pencinta drama: cari judul, ikuti drama favorit, dan **dapat notifikasi otomatis saat episode baru tayang**.

Sumber data: [TVMaze API](https://www.tvmaze.com/api) — publik, gratis, tanpa API key.

## Fitur

| Perintah | Fungsi |
|---|---|
| `/cari <judul>` | Cari drama (maks 5 hasil + ID untuk perintah lain) |
| `/detail <id>` | Sinopsis, rating, status, episode berikutnya |
| `/ikuti <id>` | Notifikasi otomatis saat episode baru tayang |
| `/list` | Daftar drama yang diikuti |
| `/berhenti <id>` | Berhenti ikuti |

Pengecekan episode berjalan otomatis tiap `CHECK_INTERVAL_HOURS` (default 6 jam), state watchlist per chat di folder `data/`.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
# Isi BOT_TOKEN dari @BotFather

python -m bot
```

## Test & demo

```powershell
pytest          # unit test tanpa network
python demo.py          # demo offline (data dummy)
python demo.py --live   # demo dengan API TVMaze asli (butuh internet)
```

## Deploy

Sama dengan bot Telegram lain: VPS + systemd, atau Railway/Render. Contoh systemd ada di repo `telegram-bot-kit` (pola identik).

## Lisensi

MIT
