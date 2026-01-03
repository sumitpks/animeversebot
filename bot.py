import os
import random
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== CHARACTERS ==================
# ALL are PHOTO file_id (AgACAg...)

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
    if len(characters) < 2:
        await update.message.reply_text("❌ Not enough characters.")
        return

    fighter1, fighter2 = random.sample(characters, 2)
    winner = random.choice([fighter1, fighter2])

    media = [
        InputMediaPhoto(
            media=fighter1["img"],
            caption=f"🔥 {fighter1['name']}  ⚔️  {fighter2['name']}"
        ),
        InputMediaPhoto(media=fighter2["img"])
    ]

    try:
        await update.message.reply_media_group(media=media)
        await update.message.reply_text(
            f"🏆 WINNER\n\n✅ {winner['name']}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ================== GET FILE ID ==================

async def getid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Send ONE image as PHOTO (not file)")

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

app.run_polling()
