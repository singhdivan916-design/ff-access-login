from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import logging
import re
import json
import os
import random
import asyncio
import time
from datetime import datetime

# ---------- HELPER: Strip emojis from button text ----------
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
# -----------------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- DIRECTLY SET YOUR BOT TOKEN HERE ----------
BOT_TOKEN = "8817070830:AAFk6xwNiU63V4QNF0V_0vgff_R5LQw3_qk"   # <-- Replace with your actual token
# -------------------------------------------------------

EMOJI_FILE = "emojis.json"

# Fallback emojis list (used if emoji not found)
FALLBACK_EMOJIS_LIST = [
    "verified", "blue_verification", "bottle", "heart", "stars",
    "diamond", "crown", "gift", "fire", "rocket", "smile",
    "thumbs", "skull", "teddy", "devil", "crying", "flex"
]

# Global store for copy button texts (key -> {"text": str, "timestamp": float})
copy_store = {}

# Load emojis from file
PREMIUM_EMOJIS = {}

def load_emojis():
    global PREMIUM_EMOJIS
    try:
        if os.path.exists(EMOJI_FILE):
            with open(EMOJI_FILE, 'r', encoding='utf-8') as f:
                PREMIUM_EMOJIS = json.load(f)
                logger.info(f"Loaded {len(PREMIUM_EMOJIS)} emojis from file")
        else:
            # If file missing, use a minimal fallback set (but we expect the file to exist)
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
            save_emojis()
    except Exception as e:
        logger.error(f"Error loading emojis: {e}")

def save_emojis():
    try:
        with open(EMOJI_FILE, 'w', encoding='utf-8') as f:
            json.dump(PREMIUM_EMOJIS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving emojis: {e}")

def get_emoji_html(name):
    data = PREMIUM_EMOJIS.get(name)
    if data:
        return f'<tg-emoji emoji-id="{data["id"]}">{data["fallback"]}</tg-emoji>'
    return ""

def get_similar_emoji(emoji):
    # Simplified mapping – expand as needed
    similar_map = {
        "😊": "smile", "❤️": "heart", "👍": "done", "⭐": "stars",
        "🔥": "fire", "🎁": "gift", "💎": "gem", "🚀": "rocket",
        "✅": "verified", "👀": "eyes", "💥": "boom", "🔝": "top",
    }
    name = similar_map.get(emoji)
    if name and name in PREMIUM_EMOJIS:
        return PREMIUM_EMOJIS[name]
    return None

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

# ---------------------- Progress bar ----------------------
def get_progress_bar(percent):
    filled = int(percent / 10)
    bar = '▓' * filled + '░' * (10 - filled)
    return f"[{bar}] {percent}%"

# ---------------------- Keyboards ----------------------
async def media_prompt_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼️ Yes, Add Media", callback_data="media_yes"),
            InlineKeyboardButton("🚫 No, Just Text", callback_data="media_no")
        ]
    ])

async def button_prompt_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Add Buttons", callback_data="btn_yes"),
            InlineKeyboardButton("❌ No, Skip Buttons", callback_data="btn_no")
        ]
    ])

async def button_type_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 URL Button", callback_data="btn_type_url"),
            InlineKeyboardButton("📋 Text Button (Copy)", callback_data="btn_type_text")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")]
    ])

async def button_colors_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵 Blue", callback_data="btn_color_primary"),
            InlineKeyboardButton("🟢 Green", callback_data="btn_color_success"),
            InlineKeyboardButton("🔴 Red", callback_data="btn_color_danger")
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="btn_back_to_type")]
    ])

# ---------------------- User data store ----------------------
user_data_store = {}

# ---------------------- Command Handlers ----------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"""<b>—͞𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐌𝐎𝐉𝐈 𝐁𝐎𝐓 ☬</b>
🏵 <b>𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 𝐏𝐑𝐄𝐌𝐈??𝐌 𝐄𝐌𝐎𝐉𝐈 𝐁𝐎𝐓</b> {get_emoji_html('verified')}

Cᴏɴᴠᴇʀᴛ Aɴʏ Nᴏʀᴍᴀʟ Eᴍᴏᴊɪ Iɴᴛᴏ {get_emoji_html('top')} Pʀᴇᴍɪᴜᴍ {get_emoji_html('verified')}

➡️ Cʜᴏᴏsᴇ Aɴ Oᴘᴛɪᴏɴ Bᴇʟᴏᴡ {get_emoji_html('heart')}

📌 <b>Commands:</b>
/make_post → Create a premium post
/cancel → Cancel current operation"""
    await update.message.reply_text(msg, parse_mode="HTML")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data_store:
        del user_data_store[user_id]
        await update.message.reply_text(f"❌ <b>Operation cancelled.</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("ℹ️ No active operation to cancel.")

async def make_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id] = {
        "step": "waiting_text",
        "buttons": [],
        "has_media": False,
        "media_type": None,
        "file_id": None
    }
    msg = f"""<b>—͞𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐌𝐎𝐉𝐈 𝐁𝐎𝐓 ☬</b>
⚠️ <b>𝗠𝗔𝗞𝗘 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗣𝗢𝗦𝗧</b> ⚠️

➡️ Sᴇɴᴅ Mᴇ Yᴏᴜʀ Pᴏsᴛ Tᴇxᴛ Nᴏᴡ {get_emoji_html('done')}
➡️ Nᴏʀᴍᴀʟ Eᴍᴏᴊɪs → Pʀᴇᴍɪᴜᴍ Aɴɪᴍᴀᴛᴇᴅ {get_emoji_html('sparkle')}
➡️ Aʟʟ Fᴏʀᴍᴀᴛᴛɪɴɢ Pʀᴇsᴇʀᴠᴇᴅ {get_emoji_html('check')}

📊 /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ"""
    await update.message.reply_text(msg, parse_mode="HTML")

# ---------------------- Callback Query Handler ----------------------
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data

    # Handle copy button clicks
    if data.startswith("copy_"):
        key = data[5:]
        if key in copy_store:
            text = copy_store[key]["text"]
            await query.message.reply_text(
                f"📋 <b>Copied text:</b>\n{text}",
                parse_mode="HTML"
            )
            del copy_store[key]
        else:
            await query.message.reply_text("❌ This copy text has expired.")
        return

    if user_id not in user_data_store:
        await query.edit_message_text("⏳ <b>Session expired. Start again with /make_post</b>", parse_mode="HTML")
        return

    if data == "media_yes":
        user_data_store[user_id]["step"] = "waiting_media"
        await query.edit_message_text(
            f"🖼️ <b>Send me any media</b> (photo, video, document, audio, etc.)\n"
            f"📸 You can also add a caption with normal emojis – they will be converted to premium.\n\n"
            f"📊 /cancel to cancel",
            parse_mode="HTML"
        )
    elif data == "media_no":
        user_data_store[user_id]["has_media"] = False
        await show_preview_and_ask_buttons(update, context, query)
        return

    elif data == "btn_yes":
        user_data_store[user_id]["step"] = "waiting_button_type"
        await query.edit_message_text(
            "🎯 <b>Select button type:</b>",
            reply_markup=await button_type_kb(),
            parse_mode="HTML"
        )
    elif data == "btn_no":
        await show_final_preview(update, context, query)
    elif data == "btn_type_url":
        user_data_store[user_id]["temp_button"] = {"type": "url"}
        user_data_store[user_id]["step"] = "waiting_button_text"
        await query.edit_message_text(
            "🔗 <b>Enter button text</b> (no limit):\nExample: Visit Website",
            parse_mode="HTML"
        )
    elif data == "btn_type_text":
        user_data_store[user_id]["temp_button"] = {"type": "text"}
        user_data_store[user_id]["step"] = "waiting_button_text"
        await query.edit_message_text(
            "📋 <b>Enter button text</b> (no limit):\nExample: Copy Code",
            parse_mode="HTML"
        )
    elif data == "btn_cancel":
        await show_final_preview(update, context, query)
    elif data == "btn_back_to_type":
        user_data_store[user_id]["step"] = "waiting_button_type"
        await query.edit_message_text(
            "🎯 <b>Select button type:</b>",
            reply_markup=await button_type_kb(),
            parse_mode="HTML"
        )
    elif data.startswith("btn_color_"):
        color = data.replace("btn_color_", "")
        user_data_store[user_id]["temp_button"]["color"] = color
        button = user_data_store[user_id].pop("temp_button")
        user_data_store[user_id]["buttons"].append(button)
        await query.edit_message_text(
            f"✅ <b>Button added!</b>\n\n"
            f"Type: {'🔗 URL' if button['type'] == 'url' else '📋 Text'}\n"
            f"Text: {button['text']}\n"
            f"Color: {color.upper()}\n\n"
            f"Do you want to add another button?\n"
            f"Send /addbutton to add more\n"
            f"Or send /donebuttons when finished",
            parse_mode="HTML"
        )
        user_data_store[user_id]["step"] = "waiting_more_buttons"
    else:
        await query.edit_message_text("❓ <b>Unknown option.</b>", parse_mode="HTML")

# ---------------------- Helper: Show preview and ask for buttons ----------------------
async def show_preview_and_ask_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    data = user_data_store[user_id]
    text = data.get("text", "")
    caption = data.get("caption", "")
    has_media = data.get("has_media", False)
    file_id = data.get("file_id")
    media_type = data.get("media_type")

    final_text = convert_normal_emojis_to_premium(text or caption)

    try:
        if has_media and file_id:
            if media_type == "photo":
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=file_id,
                    caption=final_text,
                    parse_mode="HTML"
                )
            elif media_type == "video":
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=file_id,
                    caption=final_text,
                    parse_mode="HTML"
                )
            elif media_type == "document":
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file_id,
                    caption=final_text,
                    parse_mode="HTML"
                )
            elif media_type == "audio":
                await context.bot.send_audio(
                    chat_id=update.effective_chat.id,
                    audio=file_id,
                    caption=final_text,
                    parse_mode="HTML"
                )
            elif media_type == "animation":
                await context.bot.send_animation(
                    chat_id=update.effective_chat.id,
                    animation=file_id,
                    caption=final_text,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file_id,
                    caption=final_text,
                    parse_mode="HTML"
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=final_text,
                parse_mode="HTML"
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Preview error: {e}",
            parse_mode="HTML"
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{get_emoji_html('eyes')} <b>𝗕𝗨𝗧𝗧𝗢𝗡 𝗔𝗗𝗗 𝗞𝗔𝗥𝗡𝗔 𝗖𝗛𝗔𝗛𝗧𝗘 𝗛𝗢?</b> {get_emoji_html('done')}",
        reply_markup=await button_prompt_kb(),
        parse_mode="HTML"
    )
    user_data_store[user_id]["step"] = "waiting_buttons"

# ---------------------- Helper: Show final preview with loading animation ----------------------
async def show_final_preview(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    user_id = update.effective_user.id
    data = user_data_store[user_id]
    text = data.get("text", "")
    caption = data.get("caption", "")
    has_media = data.get("has_media", False)
    file_id = data.get("file_id")
    media_type = data.get("media_type")
    buttons = data.get("buttons", [])
    original_text = data.get("original_text", text or caption)
    button_icon_id = get_emoji_id_from_text(original_text)

    final_text = convert_normal_emojis_to_premium(text or caption)
    reply_markup = None

    if buttons:
        keyboard = []
        for btn in buttons:
            btn_color = btn.get("color", "primary")
            button_text = strip_emojis(btn["text"])
            button_dict = {
                "text": button_text,
                "style": btn_color
            }
            if button_icon_id:
                button_dict["icon_custom_emoji_id"] = button_icon_id
            if btn.get("type") == "url":
                button_dict["url"] = btn["url"]
            else:
                copy_key = str(random.randint(100000, 999999))
                while copy_key in copy_store:
                    copy_key = str(random.randint(100000, 999999))
                copy_store[copy_key] = {
                    "text": btn.get("copy_text", ""),
                    "timestamp": time.time()
                }
                button_dict["callback_data"] = f"copy_{copy_key}"
            keyboard.append([InlineKeyboardButton(**button_dict)])
        reply_markup = InlineKeyboardMarkup(keyboard)

    # Loading progress
    loading_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"<b>✅ ✨ DONE ✨</b> {get_emoji_html('heart')}\n{get_progress_bar(0)}",
        parse_mode="HTML"
    )

    steps = [10, 30, 50, 70, 90, 100]
    for percent in steps:
        await asyncio.sleep(0.7)
        try:
            await loading_msg.edit_text(
                text=f"<b>✅ ✨ DONE ✨</b> {get_emoji_html('heart')}\n{get_progress_bar(percent)}",
                parse_mode="HTML"
            )
        except Exception:
            break

    await loading_msg.edit_text(
        text=f"""<b>✅ ✨ DONE ✨</b> {get_emoji_html('heart')}
{get_progress_bar(100)}
{get_emoji_html('top')} <b>𝙥𝙤𝙨𝙩 𝙧𝙚𝙖𝙙𝙮! 𝙨𝙚𝙣𝙙𝙞𝙣𝙜 𝙣𝙤𝙬</b> {get_emoji_html('rocket')}""",
        parse_mode="HTML"
    )
    await asyncio.sleep(0.5)

    # Send final post
    try:
        if has_media and file_id:
            if media_type == "photo":
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=file_id,
                    caption=final_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            elif media_type == "video":
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=file_id,
                    caption=final_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            elif media_type == "document":
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file_id,
                    caption=final_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            elif media_type == "audio":
                await context.bot.send_audio(
                    chat_id=update.effective_chat.id,
                    audio=file_id,
                    caption=final_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            elif media_type == "animation":
                await context.bot.send_animation(
                    chat_id=update.effective_chat.id,
                    animation=file_id,
                    caption=final_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            else:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file_id,
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
            text=f"""<b>✅ ✨ post created!</b> {get_emoji_html('gem')}
📣 <b>forward wherever you want</b> {get_emoji_html('top')}
🎁 share on channels & groups {get_emoji_html('gift')}""",
            parse_mode="HTML"
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ <b>Error displaying post:</b> {e}",
            parse_mode="HTML"
        )
    # Clear session
    del user_data_store[user_id]

# ---------------------- Message Handler ----------------------
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
                f"➡️ <b>𝗧𝗘𝗫𝗧 𝗦𝗔𝗩𝗘𝗗!</b> {get_emoji_html('done')}\n\n"
                f"{get_emoji_html('eyes')} <b>𝗔𝗗𝗗 𝗠𝗘𝗗𝗜𝗔?</b> {get_emoji_html('boom')}",
                reply_markup=await media_prompt_kb(),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ Please send text, not media.", parse_mode="HTML")
        return

    if step == "waiting_media":
        if update.message.photo:
            media_type = "photo"
            file_id = update.message.photo[-1].file_id
        elif update.message.video:
            media_type = "video"
            file_id = update.message.video.file_id
        elif update.message.document:
            media_type = "document"
            file_id = update.message.document.file_id
        elif update.message.audio:
            media_type = "audio"
            file_id = update.message.audio.file_id
        elif update.message.animation:
            media_type = "animation"
            file_id = update.message.animation.file_id
        else:
            await update.message.reply_text("❌ Unsupported media type. Please send a photo, video, document, audio, or GIF.", parse_mode="HTML")
            return

        user_data_store[user_id]["has_media"] = True
        user_data_store[user_id]["media_type"] = media_type
        user_data_store[user_id]["file_id"] = file_id
        user_data_store[user_id]["caption"] = update.message.caption or ""
        user_data_store[user_id]["original_text"] = user_data_store[user_id]["caption"]

        await show_preview_and_ask_buttons(update, context)
        return

    if step == "waiting_button_text":
        button_text = update.message.text.strip()
        # No length limit
        user_data_store[user_id]["temp_button"]["text"] = button_text
        user_data_store[user_id]["step"] = "waiting_button_data"
        if user_data_store[user_id]["temp_button"].get("type") == "url":
            await update.message.reply_text("🔗 Enter the URL (must start with http:// or https://):", parse_mode="HTML")
        else:
            await update.message.reply_text("📋 Enter the text to copy when button is clicked:", parse_mode="HTML")
        return

    if step == "waiting_button_data":
        btn_data = update.message.text.strip()
        if user_data_store[user_id]["temp_button"].get("type") == "url":
            if not (btn_data.startswith("http://") or btn_data.startswith("https://")):
                await update.message.reply_text("❌ Invalid URL. Must start with http:// or https://. Try again:", parse_mode="HTML")
                return
            user_data_store[user_id]["temp_button"]["url"] = btn_data
        else:
            # No length limit
            user_data_store[user_id]["temp_button"]["copy_text"] = btn_data
        user_data_store[user_id]["step"] = "waiting_button_color"
        await update.message.reply_text(
            "🎨 <b>Select button color:</b>",
            reply_markup=await button_colors_kb(),
            parse_mode="HTML"
        )
        return

    if step == "waiting_more_buttons":
        text = update.message.text.strip().lower()
        if text == "/addbutton":
            user_data_store[user_id]["step"] = "waiting_button_type"
            await update.message.reply_text(
                "🎯 <b>Select button type for another button:</b>",
                reply_markup=await button_type_kb(),
                parse_mode="HTML"
            )
        elif text == "/donebuttons":
            await show_final_preview(update, context)
        else:
            await update.message.reply_text(
                "Send /addbutton to add more buttons\nOr /donebuttons to finish",
                parse_mode="HTML"
            )
        return

    await update.message.reply_text("⏳ I'm waiting for you to complete the current step. Use /cancel to abort.", parse_mode="HTML")

# ---------------------- Webhook setup ----------------------
def create_application():
    load_emojis()
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("make_post", make_post_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("addbutton", handle_message))
    application.add_handler(CommandHandler("donebuttons", handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO | filters.ANIMATION, handle_message))

    return application

# Vercel expects an ASGI app named `app`
app = create_application().webhook_app

# For local testing (optional)
if __name__ == "__main__":
    print("Starting local polling (for development only).")
    # Uncomment below to run locally with polling
    # create_application().run_polling(allowed_updates=Update.ALL_TYPES)