import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== DUMMY WEB SERVER (REQUIRED FOR RENDER FREE) ==================

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Anime bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ================== CHARACTERS ==================

characters = [
    {"name": "Goku", "img": "AgACAgUAAxkBAAOXaVUbk-2rf55eevSR7oWaDLDw2JIAAt0MaxsMbalWE5UlbEs4sScBAAMCAAN4AAM4BA"},
    {"name": "Zenitsu", "img": "AgACAgUAAxkBAAObaVUb3AyHLvM3iMr2xBtVR767gJAAAt4MaxsMbalWXyIfCFNRfVUBAAMCAAN5AAM4BA"},
    {"name": "Naruto Uzumaki", "img": "AgACAgUAAxkBAAOTaVUbUYiN1xxJsFshidUgSC3_U20AAtsMaxsMbalWNhujsvxZ_24BAAMCAAN5AAM4BA"},
    {"name": "Gojo Satorou", "img": "AgACAgUAAxkBAAOfaVUcGBTA6rHf8mTEaNGkfftinVIAAt8MaxsMbalWWA5pJkECpzUBAAMCAAN5AAM4BA"},
    {"name": "Aizen", "img": "AgACAgUAAxkBAAN6aVUXUmfg59rAbzoqUqBRgpNwr6sAAs8MaxsMbalW0QJ8Ds9GCYIBAAMCAAN5AAM4BA"},
    {"name": "Akatsuki", "img": "AgACAgUAAxkBAAOvaVUdnY88-JUNEMc7SR7TTQYdjw4AAuUMaxsMbalWp4li3jbDgywBAAMCAAN4AAM4BA"},
    {"name": "Asta", "img": "AgACAgUAAxkBAAOzaVUd1F7NwyUxB2m7SXGFgLDQ84AAAugMaxsMbalW4XUdbmZDXjQBAAMCAAN5AAM4BA"},
    {"name": "Luffy", "img": "AgACAgUAAxkBAAPpaVUhdEc-6rqaS1ansTqohMZjwwYAAgUNaxsMbalW5EEuCdlhSmcBAAMCAAN5AAM4BA"},
    {"name": "Madara Uchiha", "img": "AgACAgUAAxkBAAPxaVUiBhcCGdg4iItVQm04V_U5zZ4AAhANaxsMbalWY0vUo-aQXIQBAAMCAAN5AAM4BA"},
    {"name": "Saitama", "img": "AgACAgUAAxkBAAIBAWlVIvmaTA5NPXBmjZXId7luIUhEAAIfDWsbDG2pVojXooqepeN5AQADAgADeQADOAQ"},
    {"name": "Zoro", "img": "AgACAgUAAxkBAAIBLWlVJT_1l_dAxLiRt_jdGgTclfCGAAJCDWsbDG2pVkNPBrqy8VVnAQADAgADeAADOAQ"}
]

# ================== COMMANDS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\nType /spin to start an anime battle 🔥"
    )

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fighter1, fighter2 = random.sample(characters, 2)
    winner = random.choice([fighter1, fighter2])

    media = [
        InputMediaPhoto(
            media=fighter1["img"],
            caption=f"🔥 {fighter1['name']}  ⚔️  {fighter2['name']}"
        ),
        InputMediaPhoto(media=fighter2["img"])
    ]

    await update.message.reply_media_group(media=media)
    await update.message.reply_text(f"🏆 WINNER\n\n✅ {winner['name']}")

# ================== GET FILE ID ==================

async def getid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Send ONE image as PHOTO")

async def getid_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text(
            f"PHOTO file_id:\n{update.message.photo[-1].file_id}"
        )

# ================== BOT SETUP ==================

TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("spin", spin))
app.add_handler(CommandHandler("getid", getid_command))
app.add_handler(MessageHandler(filters.PHOTO, getid_image))

print("🤖 BOT STARTING POLLING...")
app.run_polling()


