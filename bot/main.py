"""Entry point Drama Bot: cari drama, ikuti, notifikasi episode baru."""
from __future__ import annotations

import logging
import os
from datetime import timedelta
from functools import partial

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from bot.store import WatchlistStore
from bot.tvmaze import (
    Episode,
    format_show,
    get_show,
    new_episodes_since,
    search_shows,
)

logger = logging.getLogger(__name__)


def _load_env():
    from dotenv import load_dotenv

    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("BOT_TOKEN belum diisi. Salin .env.example menjadi .env lalu isi.")
    interval = int(os.getenv("CHECK_INTERVAL_HOURS", "6") or "6")
    return token, max(1, interval)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Saya bot asisten nonton drama.\n"
        "\nPerintah:\n"
        "/cari <judul> — cari drama\n"
        "/detail <id> — sinopsis & info lengkap\n"
        "/ikuti <id> — notifikasi saat episode baru tayang\n"
        "/list — drama yang Anda ikuti\n"
        "/berhenti <id> — berhenti ikuti\n"
        "\nContoh: /cari Queen of Tears"
    )


async def cmd_cari(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args or []).strip()
    if not query:
        await update.message.reply_text("Format: /cari <judul drama>")
        return
    await update.message.reply_text("Mencari...")
    try:
        shows = search_shows(query)
    except Exception:
        logger.exception("Gagal cari di TVMaze")
        await update.message.reply_text("Layanan pencarian sedang bermasalah, coba lagi nanti.")
        return
    if not shows:
        await update.message.reply_text(f"Tidak ketemu drama \"{query}\". Coba judul lain.")
        return
    lines = [format_show(s) for s in shows]
    await update.message.reply_text("\n\n".join(lines))


async def cmd_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Format: /detail <id> (id ada di hasil /cari)")
        return
    show = get_show(int(context.args[0]))
    if show is None:
        await update.message.reply_text("ID tidak ditemukan. Cari ulang dengan /cari.")
        return
    await update.message.reply_text(format_show(show, with_summary=True))


async def cmd_ikuti(update: Update, context: ContextTypes.DEFAULT_TYPE, store: WatchlistStore) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Format: /ikuti <id> (id ada di hasil /cari)")
        return
    show_id = int(context.args[0])
    show = get_show(show_id)
    if show is None:
        await update.message.reply_text("ID tidak ditemukan.")
        return
    chat_id = update.effective_chat.id
    # Baseline: episode yang sudah tayang tidak di-notify; mulai dari yang belum
    added = store.add(chat_id, show_id, show.name, last_airdate=show.next_airdate)
    if not added:
        await update.message.reply_text(f"{show.name} sudah ada di list Anda.")
        return
    await update.message.reply_text(
        f"Mengikuti {show.name}.\n"
        f"Saya kabari di sini saat episode baru tayang "
        f"(dicek otomatis tiap beberapa jam)."
    )


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE, store: WatchlistStore) -> None:
    data = store.list_shows(update.effective_chat.id)
    if not data:
        await update.message.reply_text("List kosong. Cari drama dengan /cari lalu /ikuti <id>.")
        return
    lines = [f"• {v['name']} (ID: {k})" for k, v in data.items()]
    await update.message.reply_text("Drama yang Anda ikuti:\n" + "\n".join(lines))


async def cmd_berhenti(update: Update, context: ContextTypes.DEFAULT_TYPE, store: WatchlistStore) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Format: /berhenti <id>")
        return
    ok = store.remove(update.effective_chat.id, int(context.args[0]))
    await update.message.reply_text("Dihapus dari list." if ok else "ID itu tidak ada di list Anda.")


async def check_new_episodes(app: Application, store: WatchlistStore) -> None:
    """Cek semua subscriber: episode baru tayang sejak `last_airdate` -> kirim notif."""
    for chat_id, shows in store.all_subscribers().items():
        for show_id_str, meta in shows.items():
            try:
                eps: list[Episode] = new_episodes_since(int(show_id_str), meta.get("last_airdate"))
            except Exception:
                logger.exception("Gagal cek show %s", show_id_str)
                continue
            if not eps:
                continue
            latest = max(ep.airdate for ep in eps if ep.airdate)
            for ep in eps:
                text = (
                    f"Episode baru tayang!\n"
                    f"{meta['name']} — S{ep.season:02d}E{ep.number:02d} {ep.name}"
                    + (f"\nTayang: {ep.airdate}" if ep.airdate else "")
                )
                try:
                    await app.bot.send_message(chat_id=chat_id, text=text)
                except Exception:
                    logger.exception("Gagal kirim notif ke %s", chat_id)
            store.set_last_airdate(chat_id, int(show_id_str), latest)


def build_application() -> tuple[Application, WatchlistStore, int]:
    token, interval_hours = _load_env()
    store = WatchlistStore()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("cari", cmd_cari))
    app.add_handler(CommandHandler("detail", cmd_detail))
    app.add_handler(CommandHandler("ikuti", partial(cmd_ikuti, store=store)))
    app.add_handler(CommandHandler("list", partial(cmd_list, store=store)))
    app.add_handler(CommandHandler("berhenti", partial(cmd_berhenti, store=store)))

    async def _job(context: ContextTypes.DEFAULT_TYPE) -> None:
        await check_new_episodes(context.application, store)

    app.job_queue.run_repeating(_job, interval=interval_hours * 3600, first=60)
    return app, store, interval_hours


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app, _, interval = build_application()
    logger.info("Drama bot mulai — cek episode baru tiap %d jam", interval)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
