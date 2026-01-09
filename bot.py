import os
import random
import time
import json
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================

ADMIN_IDS = {6752752402, 5526634074}
COOLDOWN_SECONDS = 10
user_cooldowns = {}

pending_getid = set()
pending_add_char = {}  # admin_id -> (name, universe)

DATA_FILE = "characters.json"

# ================= DEFAULT DATA =================

DEFAULT_DATA = {
    "anime": [
        {"name": "Goku", "img": "AgACAgUAAxkBAAOXaVUbk-2rf55eevSR7oWaDLDw2JIAAt0MaxsMbalWE5UlbEs4sScBAAMCAAN4AAM4BA"},
        {"name": "Zenitsu", "img": "AgACAgUAAxkBAAObaVUb3AyHLvM3iMr2xBtVR767gJAAAt4MaxsMbalWXyIfCFNRfVUBAAMCAAN5AAM4BA"},
        {"name": "Naruto Uzumaki", "img": "AgACAgUAAxkBAAOTaVUbUYiN1xxJsFshidUgSC3_U20AAtsMaxsMbalWNhujsvxZ_24BAAMCAAN5AAM4BA"},
        {"name": "Gojo Satorou", "img": "AgACAgUAAxkBAAOfaVUcGBTA6rHf8mTEaNGkfftinVIAAt8MaxsMbalWWA5pJkECpzUBAAMCAAN5AAM4BA"},
        {"name": "Aizen", "img": "AgACAgUAAxkBAAN6aVUXUmfg59rAbzoqUqBRgpNwr6sAAs8MaxsMbalW0QJ8Ds9GCYIBAAMCAAN5AAM4BA"},
        {"name": "5 Gotei Members", "img": "AgACAgUAAxkBAAN-aVUXnUUgBO-dam1dXAPzZmLD5jMAAtAMaxsMbalWbWJ5tvdJd4QBAAMCAAN4AAM4BA"},
        {"name": "Akatsuki", "img": "AgACAgUAAxkBAAOvaVUdnY88-JUNEMc7SR7TTQYdjw4AAuUMaxsMbalWp4li3jbDgywBAAMCAAN4AAM4BA"},
        {"name": "Asta", "img": "AgACAgUAAxkBAAOzaVUd1F7NwyUxB2m7SXGFgLDQ84AAAugMaxsMbalW4XUdbmZDXjQBAAMCAAN5AAM4BA"},
        {"name": "Bleach Group", "img": "AgACAgUAAxkBAAO3aVUeM8nXZ4UONAbB49LUHPg3X-0AAu0MaxsMbalWcNgIc92K0OIBAAMCAAN5AAM4BA"},
        {"name": "Cosmic Garou", "img": "AgACAgUAAxkBAAO7aVUebzEYG57LdTMvsIcRROtWUE0AAvAMaxsMbalWczsanQ3GBWEBAAMCAAN5AAM4BA"},
        {"name": "Dragon Ball Group", "img": "AgACAgUAAxkBAAO_aVUeschWlaGvmAZJjxU0tNia5FgAAvUMaxsMbalW_9sSDSye_PQBAAMCAAN5AAM4BA"},
        {"name": "Garou", "img": "AgACAgUAAxkBAAPDaVUe5-Cx9jpkpu3CJpPOjX-A97gAAvYMaxsMbalWR5A0JxC648sBAAMCAAN4AAM4BA"},
        {"name": "Garp", "img": "AgACAgUAAxkBAAPHaVUfIafVWNSRva_61XluD0Bvvy0AAvgMaxsMbalW4LS0GKOG19cBAAMCAAN5AAM4BA"},
        {"name": "Guts", "img": "AgACAgUAAxkBAAPLaVUfTTue2H-Suvi9zQtz0Si8fFEAAvoMaxsMbalWj6oGM4m9FJwBAAMCAAN5AAM4BA"},
        {"name": "Ichigo Kurosaki", "img": "AgACAgUAAxkBAAPPaVUfijlyJ-8XRHfOBCHZcGmbQFwAAvwMaxsMbalWNNgWbHFz6sIBAAMCAAN5AAM4BA"},
        {"name": "Itachi Uchiha", "img": "AgACAgUAAxkBAAPTaVUfyq-9eMWNxLfy2mjnryEse0UAAv0MaxsMbalW7c7M0pfayVMBAAMCAAN4AAM4BA"},
        {"name": "Sung Jin-Woo", "img": "AgACAgUAAxkBAAPXaVUf_rsBj0o88STJSATEBpRKghEAAv4MaxsMbalWaV8TsBKhHhQBAAMCAAN5AAM4BA"},
        {"name": "Zoro", "img": "AgACAgUAAxkBAAIBLWlVJT_1l_dAxLiRt_jdGgTclfCGAAJCDWsbDG2pVkNPBrqy8VVnAQADAgADeAODOAQ"},
        {"name": "Robin", "img": "AgACAgUAAxkBAAIBMWlVJaA_IYJ-7IOHvQhJr2QUZ9DWAAJDDWsbDG2pVue1sW047iq8AQADAgADeQADOAQ"}
    ],
    "marvel": [
        {"name": "Iron Man", "img": "PUT_FILE_ID"},
        {"name": "Thor", "img": "PUT_FILE_ID"}
    ]
}

# ================= JSON HELPERS =================

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA

data = load_data()

# ================= HELPERS =================

def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS

def get_pool(mode: str):
    if mode == "anime":
        return data["anime"]
    if mode == "marvel":
        return data["marvel"]
    if mode == "mixed":
        return data["anime"] + data["marvel"]
    return data["anime"]

# ================= USER COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Battle Bot\n\n"
        "/spin anime\n"
        "/spin marvel\n"
        "/spin mixed\n"
        "/getid"
    )

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    now = time.time()

    if now - user_cooldowns.get(uid, 0) < COOLDOWN_SECONDS:
        await update.message.reply_text("⏳ Cooldown active")
        return

    user_cooldowns[uid] = now

    mode = context.args[0].lower() if context.args else "anime"
    if mode not in ("anime", "marvel", "mixed"):
        await update.message.reply_text("❌ Use: anime | marvel | mixed")
        return

    pool = get_pool(mode)
    if len(pool) < 2:
        await update.message.reply_text("❌ Not enough characters")
        return

    c1, c2 = random.sample(pool, 2)
    winner = random.choice([c1, c2])

    media = [
        InputMediaPhoto(c1["img"], caption=f"🔥 {c1['name']} 🆚 {c2['name']}"),
        InputMediaPhoto(c2["img"]),
    ]

    await update.message.reply_media_group(media)
    await update.message.reply_text(f"🏆 WINNER: {winner['name']}")

# ================= GET FILE ID =================

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending_getid.add(update.effective_user.id)
    await update.message.reply_text("📸 Send a photo")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    uid = update.effective_user.id
    fid = update.message.photo[-1].file_id

    if uid in pending_getid:
        pending_getid.remove(uid)
        await update.message.reply_text(f"🆔 FILE_ID:\n{fid}")
        return

    if uid in pending_add_char:
        name, universe = pending_add_char.pop(uid)
        data[universe].append({"name": name, "img": fid})
        save_data(data)
        await update.message.reply_text(f"✅ {name} added to {universe}")

# ================= ADMIN =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text(
        "/addchar <name> <anime|marvel>\n"
        "/delchar <name>\n"
        "/listchar\n"
        "/setcooldown <seconds>"
    )

async def addchar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addchar <name> <anime|marvel>")
        return

    name = " ".join(context.args[:-1])
    universe = context.args[-1].lower()

    if universe not in ("anime", "marvel"):
        await update.message.reply_text("❌ Universe must be anime or marvel")
        return

    pending_add_char[update.effective_user.id] = (name, universe)
    await update.message.reply_text(f"📸 Send image for {name} ({universe})")

async def delchar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        return

    name = " ".join(context.args).lower()
    for u in ("anime", "marvel"):
        data[u] = [c for c in data[u] if c["name"].lower() != name]

    save_data(data)
    await update.message.reply_text("🗑 Character removed")

async def listchar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = "📜 Characters\n\n"
    total = 0
    for u in ("anime", "marvel"):
        text += f"{u.upper()}:\n"
        for c in data[u]:
            text += f"• {c['name']}\n"
        text += "\n"
        total += len(data[u])

    text += f"TOTAL: {total}"
    await update.message.reply_text(text)

async def setcooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global COOLDOWN_SECONDS
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        return
    try:
        COOLDOWN_SECONDS = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Enter a valid number")
        return
    await update.message.reply_text(f"⏱ Cooldown set to {COOLDOWN_SECONDS}s")

# ================= WEBHOOK =================

TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN or not PUBLIC_URL:
    raise RuntimeError("BOT_TOKEN or PUBLIC_URL missing")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("spin", spin))
app.add_handler(CommandHandler("getid", getid))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("addchar", addchar))
app.add_handler(CommandHandler("delchar", delchar))
app.add_handler(CommandHandler("listchar", listchar))
app.add_handler(CommandHandler("setcooldown", setcooldown))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

print("🤖 BOT LIVE")

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"{PUBLIC_URL}/{TOKEN}",
)
