# ============================================================
#  main.py — Invite Challenge Telegram Bot (FINAL FIXED)
# ============================================================

import os
import logging
from datetime import timedelta

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)
import telegram.error

import sheets
from config import PROMO_TIERS, CLAIM_DEADLINE, BRAND_NAME, get_channel
from messages import MESSAGES

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

WARNING_DELAY_HOURS = 24
REMOVAL_DELAY_HOURS = 24


def get_promo_for_count(count: int):
    current = None
    for min_count, promo_name in PROMO_TIERS:
        if count >= min_count:
            current = promo_name
    return current


def get_msg(lang: str, key: str) -> str:
    return MESSAGES.get(lang, MESSAGES["en"]).get(key, "")


def fmt(template: str, **kwargs) -> str:
    result = template
    for k, v in kwargs.items():
        result = result.replace(f"{{{{{k}}}}}", str(v))
    return result


# ─── /start ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "there"

    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
         InlineKeyboardButton("🇲🇽 Español", callback_data="lang_mx")],
    ]

    await update.message.reply_text(
        f"👋 Hello, *{first_name}*! Welcome to *{BRAND_NAME}*!\n\n"
        "Please choose your language:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ─── Language Selection ───────────────────────────────────────────────────────
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    sheets.set_user_language(query.from_user.id, lang)
    await query.edit_message_text(get_msg(lang, "language_set"), parse_mode="Markdown")


# ─── "invite" keyword (the part that was failing) ─────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.text.strip().lower() != "invite":
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or "user"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or username
    first_name = user.first_name or "there"

    lang = sheets.get_user_language(user_id)
    if not lang:
        await update.message.reply_text("👋 Please select your language first using /start", parse_mode="Markdown")
        return

    if sheets.get_user_invite_link(user_id):
        msg = fmt(get_msg(lang, "already_has_link"), first_name=first_name, link=sheets.get_user_invite_link(user_id))
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    channel_id = get_channel(lang)

    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=channel_id,
            name=full_name,
            creates_join_request=False,
        )
        link_url = invite.invite_link

        sheets.save_member(user_id=user_id, username=username, full_name=full_name, lang=lang, invite_link=link_url)

        msg = fmt(get_msg(lang, "invite_instruction"), first_name=first_name, link=link_url)
        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception:
        await update.message.reply_text("❌ Sorry, I couldn't create your invite link right now.\nPlease try again in a moment.")


# ─── Other commands (unchanged) ───────────────────────────────────────────────
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (keep your original status_command function)
    pass

async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (keep your original claim_command function)
    pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (keep your original help_command function)
    pass

async def track_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (keep your original track_new_member function)
    pass

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (keep your original admin_stats function)
    pass

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    logger.info("Starting bot...")
    try:
        sheets.setup_sheets()
        logger.info("Google Sheets ready.")
    except Exception as e:
        logger.error(f"Sheets init failed: {e}")
        raise

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("claim", claim_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("adminstats", admin_stats))
    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_"))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    application.add_handler(ChatMemberHandler(track_new_member, ChatMemberHandler.CHAT_MEMBER))

    application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
