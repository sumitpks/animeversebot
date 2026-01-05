import os
import random
import time
from telegram import (
    Update,
    InputMediaPhoto,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================== CONFIG ==================

ADMIN_IDS = {6752752402, 5526634074}   # ✅ ADMINS SET
COOLDOWN_SECONDS = 10
user_cooldowns = {}

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
    {"name": "Zoro", "img": "AgACAgUAAxkBAAIBLWlVJT_1l_dAxLiRt_jdGgTclfCGAAJCDWsbDG2pVkNPBrqy8VVnAQADAgADeAADOAQ"},
]

# ================== HELPERS ==================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ================== COMMANDS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "🔥 /spin – Anime Battle\n"
        "⏱️ Cooldown: 10 seconds"
    )

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    last = user_cooldowns.get(user_id, 0)
    if now - last < COOLDOWN_SECONDS:
        await update.message.reply_text(
            f"⏳ Wait {COOLDOWN_SECONDS - int(now - last)}s before spinning again."
        )
        return

    user_cooldowns[user_id] = now

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

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🆚 BATTLE 🆚", callback_data="vs")]]
    )

    await update.message.reply_text("⚔️ Battle in progress…", reply_markup=keyboard)
    await update.message.reply_text(f"🏆 WINNER\n\n✅ {winner['name']}")

async def vs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Battle already finished!")

# ================== ADMIN COMMANDS ==================

async def set_cooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /setcooldown <seconds>")
        return

    global COOLDOWN_SECONDS
    COOLDOWN_SECONDS = int(context.args[0])
    await update.message.reply_text(f"✅ Cooldown set to {COOLDOWN_SECONDS}s")

async def list_chars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = "📜 Characters:\n\n"
    for i, c in enumerate(characters, 1):
        text += f"{i}. {c['name']}\n"

    await update.message.reply_text(text)

# ================== GET FILE ID ==================

async def getid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Send ONE image as PHOTO")

async def getid_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text(
            f"PHOTO file_id:\n{update.message.photo[-1].file_id}"
        )

# ================== WEBHOOK ==================

TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN or not PUBLIC_URL:
    raise RuntimeError("BOT_TOKEN or PUBLIC_URL missing")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("spin", spin))
app.add_handler(CommandHandler("setcooldown", set_cooldown))
app.add_handler(CommandHandler("listchar", list_chars))
app.add_handler(CommandHandler("getid", getid_command))
app.add_handler(MessageHandler(filters.PHOTO, getid_image))
app.add_handler(CallbackQueryHandler(vs_callback, pattern="^vs$"))

print("🤖 Anime Battle Bot is LIVE")

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"{PUBLIC_URL}/{TOKEN}",
)
