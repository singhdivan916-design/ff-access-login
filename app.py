from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import logging
import re
import json
import os
import random
import asyncio
import time
import sys
import telegram

# ---------- Logging ----------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stderr
)
logger = logging.getLogger(__name__)
logger.info(f"python-telegram-bot version: {telegram.__version__}")

# ---------- Token ----------
BOT_TOKEN = "8817070830:AAFk6xwNiU63V4QNF0V_0vgff_R5LQw3_qk"   # <-- REPLACE THIS
if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    if not BOT_TOKEN:
        logger.error("No bot token provided!")
        sys.exit(1)

# ---------- Emoji helpers ----------
EMOJI_FILE = "emojis.json"
PREMIUM_EMOJIS = {}

def load_emojis():
    global PREMIUM_EMOJIS
    try:
        if os.path.exists(EMOJI_FILE):
            with open(EMOJI_FILE, 'r', encoding='utf-8') as f:
                PREMIUM_EMOJIS = json.load(f)
                logger.info(f"Loaded {len(PREMIUM_EMOJIS)} emojis")
        else:
            logger.warning(f"{EMOJI_FILE} not found. Using fallback.")
            PREMIUM_EMOJIS = {
                "verified": {"id": "6147565374289220368", "fallback": "✅"},
                "stars": {"id": "6235403472741603087", "fallback": "⭐"},
                "heart": {"id": "6147617184479711380", "fallback": "❤️‍🔥"},
                "done": {"id": "6274007313107915274", "fallback": "👍"},
                "top": {"id": "5463071033256848094", "fallback": "🔝"},
                "rocket": {"id": "6129639980387015660", "fallback": "🚀"},
                "gem": {"id": "6129410405795110009", "fallback": "💎"},
                "gift": {"id": "6131660826924292492", "fallback": "🎁"},
                "boom": {"id": "6129532314146838421", "fallback": "💥"},
                "eyes": {"id": "6129879029676776924", "fallback": "👀"},
                "check": {"id": "6129812419028982717", "fallback": "✅"},
                "sparkle": {"id": "6129479035077531636", "fallback": "✨"},
            }
    except Exception as e:
        logger.error(f"Error loading emojis: {e}")
        PREMIUM_EMOJIS = {"verified": {"id": "6147565374289220368", "fallback": "✅"}}

def get_emoji_html(name):
    data = PREMIUM_EMOJIS.get(name)
    return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>' if data else ""

def get_similar_emoji(emoji):
    similar_map = {
        "😊": "smile", "❤️": "heart", "👍": "done", "⭐": "stars",
        "🔥": "fire", "🎁": "gift", "💎": "gem", "🚀": "rocket",
        "✅": "verified", "👀": "eyes", "💥": "boom", "🔝": "top",
    }
    name = similar_map.get(emoji)
    if name and name in PREMIUM_EMOJIS:
        return PREMIUM_EMOJIS[name]
    return None

FALLBACK_EMOJIS_LIST = [
    "verified", "blue_verification", "bottle", "heart", "stars",
    "diamond", "crown", "gift", "fire", "rocket", "smile",
    "thumbs", "skull", "teddy", "devil", "crying", "flex"
]

def get_random_fallback_emoji():
    random_name = random.choice(FALLBACK_EMOJIS_LIST)
    return PREMIUM_EMOJIS.get(random_name, PREMIUM_EMOJIS.get("stars"))

def convert_normal_emojis_to_premium(text):
    if not text:
        return text
    emoji_pattern = re.compile(
        r'('
        r'[\U0001F1E6-\U0001F1FF]{2}|'
        r'[\U0001F600-\U0001F64F]|'
        r'[\U0001F300-\U0001F5FF]|'
        r'[\U0001F680-\U0001F6FF]|'
        r'[\U0001F700-\U0001F77F]|'
        r'[\U0001F780-\U0001F7FF]|'
        r'[\U0001F800-\U0001F8FF]|'
        r'[\U0001F900-\U0001F9FF]|'
        r'[\U0001FA70-\U0001FAFF]|'
        r'[\u2600-\u26FF]|'
        r'[\u2700-\u27BF]|'
        r'[\u2300-\u23FF]|'
        r'[\uFE0F]|'
        r'[\u200D]'
        r')+',
        flags=re.UNICODE
    )
    def replace_emoji(match):
        emoji = match.group(0)
        for name, data in PREMIUM_EMOJIS.items():
            if data["fallback"] == emoji:
                return f'<tg-emoji emoji-id="{data["id"]}">{emoji}</tg-emoji>'
        similar = get_similar_emoji(emoji)
        if similar:
            return f'<tg-emoji emoji-id="{similar["id"]}">{emoji}</tg-emoji>'
        fallback = get_random_fallback_emoji()
        return f'<tg-emoji emoji-id="{fallback["id"]}">{fallback["fallback"]}</tg-emoji>'
    return emoji_pattern.sub(replace_emoji, text)

def strip_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        r'['
        r'\U0001F1E6-\U0001F1FF\U0001F600-\U0001F64F\U0001F300-\U0001F5FF'
        r'\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF'
        r'\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF'
        r'\u2600-\u26FF\u2700-\u27BF\u2300-\u23FF\uFE0F\u200D'
        r']+',
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text).strip()

def get_emoji_id_from_text(text):
    if not text:
        return PREMIUM_EMOJIS.get("verified", {}).get("id")
    emoji_pattern = re.compile(
        r'('
        r'[\U0001F1E6-\U0001F1FF]{2}|'
        r'[\U0001F600-\U0001F64F]|'
        r'[\U0001F300-\U0001F5FF]|'
        r'[\U0001F680-\U0001F6FF]|'
        r'[\U0001F700-\U0001F77F]|'
        r'[\U0001F780-\U0001F7FF]|'
        r'[\U0001F800-\U0001F8FF]|'
        r'[\U0001F900-\U0001F9FF]|'
        r'[\U0001FA70-\U0001FAFF]|'
        r'[\u2600-\u26FF]|'
        r'[\u2700-\u27BF]|'
        r'[\u2300-\u23FF]|'
        r'[\uFE0F]|'
        r'[\u200D]'
        r')+',
        flags=re.UNICODE
    )
    emojis_found = emoji_pattern.findall(text)
    if emojis_found:
        for emoji in emojis_found:
            for name, data in PREMIUM_EMOJIS.items():
                if data["fallback"] == emoji:
                    return data["id"]
        for emoji in emojis_found:
            similar = get_similar_emoji(emoji)
            if similar:
                return similar["id"]
    return PREMIUM_EMOJIS.get("verified", {}).get("id")

# ---------- Progress bar ----------
def get_progress_bar(percent):
    filled = int(percent / 10)
    bar = '▓' * filled + '░' * (10 - filled)
    return f"[{bar}] {percent}%"

# ---------- Keyboards ----------
async def media_prompt_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼️ Yes, Add Media", callback_data="media_yes"),
         InlineKeyboardButton("🚫 No, Just Text", callback_data="media_no")]
    ])

async def button_prompt_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Add Buttons", callback_data="btn_yes"),
         InlineKeyboardButton("❌ No, Skip Buttons", callback_data="btn_no")]
    ])

async def button_type_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 URL Button", callback_data="btn_type_url"),
         InlineKeyboardButton("📋 Text Button (Copy)", callback_data="btn_type_text")],
        [InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")]
    ])

async def button_colors_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Blue", callback_data="btn_color_primary"),
         InlineKeyboardButton("🟢 Green", callback_data="btn_color_success"),
         InlineKeyboardButton("🔴 Red", callback_data="btn_color_danger")],
        [InlineKeyboardButton("⬅️ Back", callback_data="btn_back_to_type")]
    ])

# ---------- User store ----------
user_data_store = {}
copy_store = {}

# ---------- Command handlers ----------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"<b>—͞𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐌𝐎𝐉𝐈 𝐁𝐎𝐓 ☬</b>\n"
        f"🏵 <b>Welcome</b> {get_emoji_html('verified')}\n"
        f"Use /make_post to create a premium post.",
        parse_mode="HTML"
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data_store:
        del user_data_store[user_id]
        await update.message.reply_text("❌ Cancelled.", parse_mode="HTML")
    else:
        await update.message.reply_text("ℹ️ Nothing to cancel.")

async def make_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id] = {
        "step": "waiting_text",
        "buttons": [],
        "has_media": False,
        "media_type": None,
        "file_id": None
    }
    await update.message.reply_text(
        f"<b>—͞𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐌𝐎𝐉𝐈 𝐁𝐎𝐓 ☬</b>\n"
        f"⚠️ <b>MAKE PREMIUM POST</b> ⚠️\n\n"
        f"➡️ Send your text (emojis → premium) {get_emoji_html('done')}\n"
        f"📊 /cancel to cancel",
        parse_mode="HTML"
    )

# ---------- Callback handler ----------
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data

    if data.startswith("copy_"):
        key = data[5:]
        if key in copy_store:
            await query.message.reply_text(f"📋 <b>Copied:</b>\n{copy_store[key]['text']}", parse_mode="HTML")
            del copy_store[key]
        else:
            await query.message.reply_text("❌ Expired.")
        return

    if user_id not in user_data_store:
        await query.edit_message_text("⏳ Session expired. Start /make_post again.", parse_mode="HTML")
        return

    if data == "media_yes":
        user_data_store[user_id]["step"] = "waiting_media"
        await query.edit_message_text("🖼️ Send any media (photo/video/doc/audio/GIF).", parse_mode="HTML")
    elif data == "media_no":
        user_data_store[user_id]["has_media"] = False
        await show_preview_and_ask_buttons(update, context, query)
    elif data == "btn_yes":
        user_data_store[user_id]["step"] = "waiting_button_type"
        await query.edit_message_text("🎯 Select button type:", reply_markup=await button_type_kb(), parse_mode="HTML")
    elif data == "btn_no":
        await show_final_preview(update, context, query)
    elif data == "btn_type_url":
        user_data_store[user_id]["temp_button"] = {"type": "url"}
        user_data_store[user_id]["step"] = "waiting_button_text"
        await query.edit_message_text("🔗 Enter button text (no limit):", parse_mode="HTML")
    elif data == "btn_type_text":
        user_data_store[user_id]["temp_button"] = {"type": "text"}
        user_data_store[user_id]["step"] = "waiting_button_text"
        await query.edit_message_text("📋 Enter button text:", parse_mode="HTML")
    elif data == "btn_cancel":
        await show_final_preview(update, context, query)
    elif data == "btn_back_to_type":
        user_data_store[user_id]["step"] = "waiting_button_type"
        await query.edit_message_text("🎯 Select button type:", reply_markup=await button_type_kb(), parse_mode="HTML")
    elif data.startswith("btn_color_"):
        color = data.replace("btn_color_", "")
        user_data_store[user_id]["temp_button"]["color"] = color
        button = user_data_store[user_id].pop("temp_button")
        user_data_store[user_id]["buttons"].append(button)
        await query.edit_message_text(
            f"✅ Button added!\nType: {button['type']}\nText: {button['text']}\nColor: {color.upper()}\n\n"
            f"Send /addbutton to add more\nSend /donebuttons to finish",
            parse_mode="HTML"
        )
        user_data_store[user_id]["step"] = "waiting_more_buttons"
    else:
        await query.edit_message_text("❓ Unknown.", parse_mode="HTML")

# ---------- Helpers for preview and final ----------
async def show_preview_and_ask_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    data = user_data_store[user_id]
    text = data.get("text", "") or data.get("caption", "")
    final_text = convert_normal_emojis_to_premium(text)
    # Send preview
    await context.bot.send_message(chat_id=update.effective_chat.id, text=final_text, parse_mode="HTML")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{get_emoji_html('eyes')} <b>Add buttons?</b> {get_emoji_html('done')}",
        reply_markup=await button_prompt_kb(),
        parse_mode="HTML"
    )
    user_data_store[user_id]["step"] = "waiting_buttons"

async def show_final_preview(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    data = user_data_store[user_id]
    text = data.get("text", "") or data.get("caption", "")
    final_text = convert_normal_emojis_to_premium(text)
    buttons = data.get("buttons", [])
    reply_markup = None
    if buttons:
        keyboard = []
        icon_id = get_emoji_id_from_text(text)
        for btn in buttons:
            btn_dict = {
                "text": strip_emojis(btn["text"]),
                "style": btn.get("color", "primary")
            }
            if icon_id:
                btn_dict["icon_custom_emoji_id"] = icon_id
            if btn["type"] == "url":
                btn_dict["url"] = btn["url"]
            else:
                key = str(random.randint(100000, 999999))
                while key in copy_store:
                    key = str(random.randint(100000, 999999))
                copy_store[key] = {"text": btn.get("copy_text", ""), "timestamp": time.time()}
                btn_dict["callback_data"] = f"copy_{key}"
            keyboard.append([InlineKeyboardButton(**btn_dict)])
        reply_markup = InlineKeyboardMarkup(keyboard)

    # Loading animation
    loading = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"<b>✅ ✨ DONE ✨</b> {get_emoji_html('heart')}\n{get_progress_bar(0)}",
        parse_mode="HTML"
    )
    for pct in [10, 30, 50, 70, 90, 100]:
        await asyncio.sleep(0.7)
        try:
            await loading.edit_text(
                f"<b>✅ ✨ DONE ✨</b> {get_emoji_html('heart')}\n{get_progress_bar(pct)}",
                parse_mode="HTML"
            )
        except:
            pass
    await loading.edit_text(
        f"<b>✅ ✨ DONE ✨</b> {get_emoji_html('heart')}\n{get_progress_bar(100)}\n"
        f"{get_emoji_html('top')} <b>post ready!</b> {get_emoji_html('rocket')}",
        parse_mode="HTML"
    )
    await asyncio.sleep(0.5)

    # Send final
    if data.get("has_media") and data.get("file_id"):
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=data["file_id"],
            caption=final_text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=final_text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"<b>✅ post created!</b> {get_emoji_html('gem')}\n📣 forward wherever you want",
        parse_mode="HTML"
    )
    del user_data_store[user_id]

# ---------- Message handler ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data_store:
        return
    step = user_data_store[user_id].get("step")

    if step == "waiting_text":
        if update.message.text:
            user_data_store[user_id]["text"] = update.message.text
            user_data_store[user_id]["original_text"] = update.message.text
            await update.message.reply_text(
                f"➡️ <b>Text saved!</b> {get_emoji_html('done')}\n\n"
                f"{get_emoji_html('eyes')} <b>Add media?</b>",
                reply_markup=await media_prompt_kb(),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ Send text.")
        return

    if step == "waiting_media":
        if update.message.photo:
            media_type, file_id = "photo", update.message.photo[-1].file_id
        elif update.message.video:
            media_type, file_id = "video", update.message.video.file_id
        elif update.message.document:
            media_type, file_id = "document", update.message.document.file_id
        elif update.message.audio:
            media_type, file_id = "audio", update.message.audio.file_id
        elif update.message.animation:
            media_type, file_id = "animation", update.message.animation.file_id
        else:
            await update.message.reply_text("❌ Unsupported media.")
            return
        user_data_store[user_id]["has_media"] = True
        user_data_store[user_id]["media_type"] = media_type
        user_data_store[user_id]["file_id"] = file_id
        user_data_store[user_id]["caption"] = update.message.caption or ""
        user_data_store[user_id]["original_text"] = user_data_store[user_id]["caption"]
        await show_preview_and_ask_buttons(update, context)
        return

    if step == "waiting_button_text":
        user_data_store[user_id]["temp_button"]["text"] = update.message.text.strip()
        user_data_store[user_id]["step"] = "waiting_button_data"
        if user_data_store[user_id]["temp_button"].get("type") == "url":
            await update.message.reply_text("🔗 Enter URL (http:// or https://):")
        else:
            await update.message.reply_text("📋 Enter text to copy:")
        return

    if step == "waiting_button_data":
        btn_data = update.message.text.strip()
        if user_data_store[user_id]["temp_button"].get("type") == "url":
            if not btn_data.startswith(("http://", "https://")):
                await update.message.reply_text("❌ Invalid URL. Try again:")
                return
            user_data_store[user_id]["temp_button"]["url"] = btn_data
        else:
            user_data_store[user_id]["temp_button"]["copy_text"] = btn_data
        user_data_store[user_id]["step"] = "waiting_button_color"
        await update.message.reply_text("🎨 Select color:", reply_markup=await button_colors_kb(), parse_mode="HTML")
        return

    if step == "waiting_more_buttons":
        if update.message.text.strip().lower() == "/addbutton":
            user_data_store[user_id]["step"] = "waiting_button_type"
            await update.message.reply_text("🎯 Button type:", reply_markup=await button_type_kb(), parse_mode="HTML")
        elif update.message.text.strip().lower() == "/donebuttons":
            await show_final_preview(update, context)
        else:
            await update.message.reply_text("Send /addbutton or /donebuttons")
        return

# ---------- Build application ----------
def create_application():
    load_emojis()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("make_post", make_post_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("addbutton", handle_message))
    app.add_handler(CommandHandler("donebuttons", handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO | filters.ANIMATION, handle_message))
    return app

# ---------- Vercel entry point ----------
logger.info("Initializing bot...")
_app = create_application()

# Safely build the ASGI app – never directly use .webhook_app without fallback
try:
    app = _app.webhook_app
    logger.info("Using app.webhook_app")
except AttributeError:
    logger.warning("webhook_app missing, using _build_webhook_app()")
    app = _app._build_webhook_app()
    logger.info("Built webhook app via _build_webhook_app()")

logger.info("Bot initialized successfully.")

# For local testing (optional)
if __name__ == "__main__":
    print("Starting local polling...")
    create_application().run_polling(allowed_updates=Update.ALL_TYPES)
