import os
import random
import time
from telegram import (
    Update,
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

ADMIN_IDS = {6752752402, 5526634074}
COOLDOWN_SECONDS = 10
user_cooldowns = {}

pending_add_char = {}  # admin_id -> character_name

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

# ================== USER COMMANDS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Anime Battle Bot!\n\n"
        "🔥 /spin – Start battle\n"
        "⏱ Cooldown enabled"
    )

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    last = user_cooldowns.get(user_id, 0)
    remaining = COOLDOWN_SECONDS - int(now - last)

    if remaining > 0:
        await update.message.reply_text(f"⏳ Wait {remaining}s before next spin.")
        return

    user_cooldowns[user_id] = now

    fighter1, fighter2 = random.sample(characters, 2)
    winner = random.choice([fighter1, fighter2])

    # First image
    await update.message.reply_photo(fighter1["img"], caption=f"🔥 {fighter1['name']}")

    # VS
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🆚 VS 🆚", callback_data="vs")]]
    )
    await update.message.reply_text(
        f"⚔️ {fighter1['name']}  VS  {fighter2['name']}",
        reply_markup=keyboard
    )

    # Second image
    await update.message.reply_photo(fighter2["img"], caption=f"🔥 {fighter2['name']}")

    # Winner
    await update.message.reply_text(f"🏆 WINNER\n\n✅ {winner['name']}")

async def vs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Battle already finished!")

# ================== ADMIN PANEL ==================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only.")
        return

    await update.message.reply_text(
        "🛠 ADMIN PANEL\n\n"
        "/addchar <name>\n"
        "/delchar <name>\n"
        "/listchar\n"
        "/setcooldown <seconds>"
    )

async def addchar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /addchar <character name>")
        return

    name = " ".join(context.args)
    pending_add_char[update.effective_user.id] = name
    await update.message.reply_text(f"📸 Send photo for **{name}**")

async def receive_char_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in pending_add_char:
        return

    name = pending_add_char.pop(user_id)
    file_id = update.message.photo[-1].file_id

    characters.append({"name": name, "img": file_id})
    await update.message.reply_text(f"✅ Character **{name}** added!")

async def delchar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /delchar <name>")
        return

    name = " ".join(context.args)
    global characters
    characters = [c for c in characters if c["name"].lower() != name.lower()]

    await update.message.reply_text(f"🗑 Character **{name}** removed.")

async def listchar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = "📜 Characters:\n\n"
    for i, c in enumerate(characters, 1):
        text += f"{i}. {c['name']}\n"

    await update.message.reply_text(text)

async def setcooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /setcooldown <seconds>")
        return

    global COOLDOWN_SECONDS
    COOLDOWN_SECONDS = int(context.args[0])
    await update.message.reply_text(f"⏱ Cooldown set to {COOLDOWN_SECONDS}s")

# ================== WEBHOOK ==================

TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN or not PUBLIC_URL:
    raise RuntimeError("BOT_TOKEN or PUBLIC_URL missing")

app = ApplicationBuilder().token(TOKEN).build()

# User
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("spin", spin))
app.add_handler(CallbackQueryHandler(vs_callback, pattern="^vs$"))

# Admin
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CommandHandler("addchar", addchar))
app.add_handler(CommandHandler("delchar", delchar))
app.add_handler(CommandHandler("listchar", listchar))
app.add_handler(CommandHandler("setcooldown", setcooldown))

# Photo handler (for addchar)
app.add_handler(MessageHandler(filters.PHOTO, receive_char_photo))

print("🤖 Anime Battle Bot is LIVE")

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"{PUBLIC_URL}/{TOKEN}",
)
