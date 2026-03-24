# ============================================================
#  main.py — Invite Challenge Telegram Bot
# ============================================================

import os
import logging
from datetime import timedelta

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


# ─── Helpers ─────────────────────────────────────────────────────────────────

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
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it"),
        ],
        [
            InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
            InlineKeyboardButton("🇲🇽 Español", callback_data="lang_mx"),
        ],
    ]

    welcome = (
        f"👋 Hello, *{first_name}*! Welcome to *{BRAND_NAME}*!\n\n"
        "Ciao! / Bonjour! / ¡Hola!\n\n"
        "🌍 Please choose your language:\n"
        "Scegli la lingua / Choisissez votre langue / Elige tu idioma:"
    )
    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ─── Language Selection ───────────────────────────────────────────────────────

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[1]
    user = query.from_user

    sheets.set_user_language(user.id, lang)

    await query.edit_message_text(
        get_msg(lang, "language_set"),
        parse_mode="Markdown",
    )


# ─── Inactivity Jobs ─────────────────────────────────────────────────────────

async def send_inactivity_warning(context: ContextTypes.DEFAULT_TYPE):
    """Fires 24h after invite link issued — warns if still 0 invites."""
    data = context.job.data
    user_id = data["user_id"]
    lang = data["lang"]
    link = data["link"]
    first_name = data["first_name"]

    if sheets.get_invite_count(user_id) > 0:
        return
    if not sheets.get_user_invite_link(user_id):
        return

    try:
        msg = fmt(get_msg(lang, "inactivity_warning"), first_name=first_name, link=link)
        await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
        logger.info(f"Inactivity warning sent to {user_id}")

        # Schedule link removal 24h after warning
        context.job_queue.run_once(
            remove_inactive_link,
            when=timedelta(hours=REMOVAL_DELAY_HOURS),
            data={"user_id": user_id, "lang": lang, "first_name": first_name, "channel_id": data["channel_id"], "link": link},
            name=f"remove_{user_id}",
        )
    except Exception as e:
        logger.warning(f"Could not warn {user_id}: {e}")


async def remove_inactive_link(context: ContextTypes.DEFAULT_TYPE):
    """Fires 24h after warning — removes link if still 0 invites."""
    data = context.job.data
    user_id = data["user_id"]
    lang = data["lang"]
    first_name = data["first_name"]
    channel_id = data["channel_id"]
    link_url = data["link"]

    if sheets.get_invite_count(user_id) > 0:
        return
    if not sheets.get_user_invite_link(user_id):
        return

    # Revoke on Telegram
    try:
        await context.bot.revoke_chat_invite_link(chat_id=channel_id, invite_link=link_url)
    except Exception as e:
        logger.warning(f"Could not revoke link on Telegram for {user_id}: {e}")

    # Remove from sheets
    sheets.remove_invite_link(user_id)
    logger.info(f"Invite link removed for inactive user {user_id}")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=get_msg(lang, "link_removed"),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning(f"Could not notify {user_id} of removal: {e}")


# ─── "invite" keyword ────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.message.text.strip().lower() != "invite":
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or "user"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or username
    first_name = user.first_name or "there"

    lang = sheets.get_user_language(user_id)
    if not lang:
        await update.message.reply_text(
            "👋 Please select your language first using /start",
            parse_mode="Markdown",
        )
        return

    existing_link = sheets.get_user_invite_link(user_id)
    if existing_link:
        msg = fmt(get_msg(lang, "already_has_link"), first_name=first_name, link=existing_link)
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

        sheets.save_member(
            user_id=user_id,
            username=username,
            full_name=full_name,
            lang=lang,
            invite_link=link_url,
        )

        msg = fmt(get_msg(lang, "invite_instruction"), first_name=first_name, link=link_url)
        await update.message.reply_text(msg, parse_mode="Markdown")
        logger.info(f"Link created for {username} ({user_id}) lang={lang}")

        # Schedule 24h inactivity warning
        context.job_queue.run_once(
            send_inactivity_warning,
            when=timedelta(hours=WARNING_DELAY_HOURS),
            data={
                "user_id": user_id,
                "lang": lang,
                "link": link_url,
                "first_name": first_name,
                "channel_id": channel_id,
            },
            name=f"warn_{user_id}",
        )

    except Exception as e:
        logger.error(f"Error creating link for {user_id}: {e}")
        await update.message.reply_text(
            "❌ Something went wrong. Please try again in a moment."
        )


# ─── /status ─────────────────────────────────────────────────────────────────

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "there"
    lang = sheets.get_user_language(user_id) or "en"

    if not sheets.get_user_invite_link(user_id):
        await update.message.reply_text(get_msg(lang, "status_no_link"), parse_mode="Markdown")
        return

    count = sheets.get_invite_count(user_id)
    promo = get_promo_for_count(count) or "—"

    msg = fmt(get_msg(lang, "status"), first_name=first_name, count=count, promo=promo)
    await update.message.reply_text(msg, parse_mode="Markdown")


# ─── /claim ──────────────────────────────────────────────────────────────────

async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or "user"
    first_name = user.first_name or "there"
    lang = sheets.get_user_language(user_id) or "en"

    already = sheets.get_claimed_promo(user_id)
    if already:
        await update.message.reply_text(
            fmt(get_msg(lang, "claim_already"), code=already), parse_mode="Markdown"
        )
        return

    count = sheets.get_invite_count(user_id)
    promo_name = get_promo_for_count(count)

    if not promo_name:
        await update.message.reply_text(get_msg(lang, "claim_not_eligible"), parse_mode="Markdown")
        return

    promo_code = promo_name  # ← replace with real codes in config.py when ready
    sheets.save_claim(user_id, username, promo_name, promo_code)

    msg = fmt(
        get_msg(lang, "claim_eligible"),
        first_name=first_name,
        promo=promo_name,
        code=promo_code,
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    logger.info(f"{username} ({user_id}) claimed {promo_name}")


# ─── /help ───────────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = sheets.get_user_language(update.effective_user.id) or "en"
    await update.message.reply_text(get_msg(lang, "help"), parse_mode="Markdown")


# ─── Channel join tracker ─────────────────────────────────────────────────────

async def track_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    joined = result.new_chat_member.status in ("member", "administrator", "creator")
    was_outside = result.old_chat_member.status in ("left", "kicked", "restricted")

    if not (joined and was_outside):
        return

    invite_link_obj = result.invite_link
    if not invite_link_obj:
        return

    owner_id = sheets.get_link_owner(invite_link_obj.invite_link)
    if not owner_id:
        return

    new_count = sheets.increment_invite_count(owner_id)
    logger.info(f"User {owner_id} now has {new_count} invites")

    thresholds = {t[0] for t in PROMO_TIERS}
    if new_count in thresholds:
        lang = sheets.get_user_language(owner_id) or "en"
        promo = get_promo_for_count(new_count)
        try:
            await context.bot.send_message(
                chat_id=owner_id,
                text=fmt(
                    get_msg(lang, "threshold_reached"),
                    first_name="",
                    promo=promo,
                    deadline=CLAIM_DEADLINE,
                ),
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Could not notify {owner_id}: {e}")


# ─── Admin ────────────────────────────────────────────────────────────────────

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        members = sheets.get_worksheet("Members").get_all_values()
        claims = sheets.get_worksheet("Claims").get_all_values()
        await update.message.reply_text(
            f"📊 *Admin Stats*\n\n"
            f"👥 Total members: *{max(0, len(members)-1)}*\n"
            f"🎁 Total claims: *{max(0, len(claims)-1)}*",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    logger.info("Starting bot...")

    # Setup Google Sheets
    try:
        sheets.setup_sheets()
        logger.info("Google Sheets ready.")
    except Exception as e:
        logger.error(f"Sheets init failed: {e}")
        raise

    # Build modern v20+ Application (no Updater!)
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("claim", claim_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("adminstats", admin_stats))
    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_"))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    application.add_handler(ChatMemberHandler(track_new_member, ChatMemberHandler.CHAT_MEMBER))

    logger.info("Bot polling started (v20+)...")
    application.run_polling(
        drop_pending_updates=True,      # ← important: clean start
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
