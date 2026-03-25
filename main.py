# ============================================================
#  main.py — Invite Challenge Telegram Bot
# ============================================================

import os
import logging
from datetime import datetime, timedelta
from html import escape

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

import sheets
from config import (
    PROMO_TIERS, CLAIM_DEADLINE, BRAND_NAME,
    CAMPAIGN_ACTIVE, MAX_INVITERS, CHECK_PROFILE_PHOTO,
    CHECK_ACCOUNT_AGE, MIN_ACCOUNT_AGE_HOURS,
    get_channel,
)
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
HTML = "HTML"


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
    safe = {k: (v if k == "link" else escape(str(v))) for k, v in kwargs.items()}
    return template.format(**safe)


async def has_profile_photo(bot, user_id: int) -> bool:
    """Returns True if the user has at least one profile photo."""
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        return photos.total_count > 0
    except Exception as e:
        logger.warning(f"Could not check profile photo for {user_id}: {e}")
        return True  # fail open — don't block if check itself fails


def estimate_account_age_hours(user_id: int) -> float:
    """
    Estimates account age in hours based on Telegram's sequential user IDs.
    This is a heuristic — not perfectly precise, but reliable enough to flag
    very new accounts (created in the last few hours).
    Returns a large number (99999) if the account appears old/unknown.
    """
    # Known approximate (user_id, creation_date) checkpoints
    checkpoints = [
        (2768409,    datetime(2013, 6,  1)),
        (100000000,  datetime(2016, 1,  1)),
        (1000000000, datetime(2020, 6,  1)),
        (1500000000, datetime(2021, 6,  1)),
        (2000000000, datetime(2022, 6,  1)),
        (6000000000, datetime(2023, 6,  1)),
        (7500000000, datetime(2024, 6,  1)),
        (9000000000, datetime(2025, 1,  1)),
    ]

    lower_date = datetime(2013, 1, 1)
    upper_date = datetime.utcnow()

    for cp_id, cp_date in checkpoints:
        if user_id >= cp_id:
            lower_date = cp_date
        else:
            upper_date = cp_date
            break

    estimated_date = lower_date + (upper_date - lower_date) / 2
    age_hours = (datetime.utcnow() - estimated_date).total_seconds() / 3600
    return age_hours


def is_account_too_new(user_id: int) -> bool:
    """
    Returns True if the account is likely younger than MIN_ACCOUNT_AGE_HOURS.
    Uses two signals:
      1. ID-based age estimate (catches brand-new accounts reliably)
      2. FirstSeen sheet record (exact timestamp of first bot interaction)
    Blocks only if BOTH signals indicate the account is too new, to avoid
    false positives from the heuristic alone.
    """
    # Signal 1: ID heuristic
    estimated_age = estimate_account_age_hours(user_id)
    id_too_new = estimated_age < MIN_ACCOUNT_AGE_HOURS

    if not id_too_new:
        # ID estimate says it's old enough — trust it and allow
        return False

    # Signal 2: Check our own first-seen record
    first_seen = sheets.get_first_seen(user_id)
    if first_seen is None:
        # Never seen before — record now and treat as new
        sheets.record_first_seen(user_id)
        return True

    hours_since_first_seen = (datetime.utcnow() - first_seen).total_seconds() / 3600
    if hours_since_first_seen < MIN_ACCOUNT_AGE_HOURS:
        return True

    return False


# ─── /start ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = escape(user.first_name or "there")
    lang = sheets.get_user_language(user.id) or "en"

    # Record first time this user touches the bot
    sheets.record_first_seen(user.id)

    # Campaign ended — show message instead of language picker
    if not CAMPAIGN_ACTIVE:
        await update.message.reply_text(
            get_msg(lang, "campaign_ended"), parse_mode=HTML
        )
        return

    keyboard = [
        [InlineKeyboardButton("🇬🇧 English",  callback_data="lang_en"),
         InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
         InlineKeyboardButton("🇲🇽 Español",  callback_data="lang_mx")],
    ]

    await update.message.reply_text(
        f"👋 Hello, <b>{first_name}</b>! Welcome to <b>{BRAND_NAME}</b>!\n\n"
        "Please choose your language / Scegli la lingua / "
        "Choisissez votre langue / Elige tu idioma:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=HTML,
    )


# ─── Language Selection ───────────────────────────────────────────────────────

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    sheets.set_user_language(query.from_user.id, lang)
    await query.edit_message_text(get_msg(lang, "language_set"), parse_mode=HTML)


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

    # Record first time this user touches the bot
    sheets.record_first_seen(user_id)

    lang = sheets.get_user_language(user_id)
    if not lang:
        await update.message.reply_text(
            "👋 Please select your language first using /start", parse_mode=HTML
        )
        return

    # ── Campaign ended check ──────────────────────────────────────────────────
    if not CAMPAIGN_ACTIVE:
        await update.message.reply_text(get_msg(lang, "campaign_ended"), parse_mode=HTML)
        return

    # ── Already has a link ────────────────────────────────────────────────────
    existing_link = sheets.get_user_invite_link(user_id)
    if existing_link:
        await update.message.reply_text(
            fmt(get_msg(lang, "already_has_link"), first_name=first_name, link=existing_link),
            parse_mode=HTML,
        )
        return

    # ── Max inviters check ────────────────────────────────────────────────────
    if MAX_INVITERS > 0:
        current_inviters = sheets.count_active_inviters()
        if current_inviters >= MAX_INVITERS:
            await update.message.reply_text(
                get_msg(lang, "campaign_full"), parse_mode=HTML
            )
            logger.info(f"Max inviters reached ({MAX_INVITERS}). Blocked {username} ({user_id})")
            return

    # ── Alt account check (profile photo) ────────────────────────────────────
    if CHECK_PROFILE_PHOTO:
        has_photo = await has_profile_photo(context.bot, user_id)
        if not has_photo:
            await update.message.reply_text(
                get_msg(lang, "alt_account_blocked"), parse_mode=HTML
            )
            logger.info(f"Alt account blocked (no photo): {username} ({user_id})")
            return

    # ── Create invite link ────────────────────────────────────────────────────
    channel_id = get_channel(lang)

    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=channel_id,
            name=full_name,
            creates_join_request=False,
        )
        link_url = invite.invite_link

        sheets.save_member(
            user_id=user_id, username=username,
            full_name=full_name, lang=lang, invite_link=link_url,
        )

        await update.message.reply_text(
            fmt(get_msg(lang, "invite_instruction"), first_name=first_name, link=link_url),
            parse_mode=HTML,
        )
        logger.info(f"Link created for {username} ({user_id}) lang={lang}")

        # Schedule 24h inactivity warning
        context.job_queue.run_once(
            send_inactivity_warning,
            when=timedelta(hours=WARNING_DELAY_HOURS),
            data={
                "user_id": user_id, "lang": lang,
                "link": link_url, "first_name": first_name,
                "channel_id": channel_id,
            },
            name=f"warn_{user_id}",
        )

    except Exception as e:
        logger.error(f"Invite link failed for {user_id}: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't create your invite link right now. Please try again in a moment."
        )


# ─── Inactivity Jobs ─────────────────────────────────────────────────────────

async def send_inactivity_warning(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    user_id = data["user_id"]

    if sheets.get_invite_count(user_id) > 0 or not sheets.get_user_invite_link(user_id):
        return

    try:
        msg = fmt(
            get_msg(data["lang"], "inactivity_warning"),
            first_name=data["first_name"],
            link=data["link"],
        )
        await context.bot.send_message(chat_id=user_id, text=msg, parse_mode=HTML)
        logger.info(f"Inactivity warning sent to {user_id}")

        context.job_queue.run_once(
            remove_inactive_link,
            when=timedelta(hours=REMOVAL_DELAY_HOURS),
            data=data,
            name=f"remove_{user_id}",
        )
    except Exception as e:
        logger.warning(f"Could not warn {user_id}: {e}")


async def remove_inactive_link(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    user_id = data["user_id"]
    lang = data["lang"]
    channel_id = data["channel_id"]
    link_url = data["link"]

    if sheets.get_invite_count(user_id) > 0 or not sheets.get_user_invite_link(user_id):
        return

    try:
        await context.bot.revoke_chat_invite_link(chat_id=channel_id, invite_link=link_url)
    except Exception as e:
        logger.warning(f"Could not revoke link for {user_id}: {e}")

    sheets.remove_invite_link(user_id)
    logger.info(f"Link removed for inactive user {user_id}")

    try:
        await context.bot.send_message(
            chat_id=user_id, text=get_msg(lang, "link_removed"), parse_mode=HTML
        )
    except Exception as e:
        logger.warning(f"Could not notify {user_id} of removal: {e}")


# ─── /status ─────────────────────────────────────────────────────────────────

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "there"
    lang = sheets.get_user_language(user_id) or "en"

    if not sheets.get_user_invite_link(user_id):
        await update.message.reply_text(get_msg(lang, "status_no_link"), parse_mode=HTML)
        return

    count = sheets.get_invite_count(user_id)
    promo = get_promo_for_count(count) or "—"

    await update.message.reply_text(
        fmt(get_msg(lang, "status"), first_name=first_name, count=count, promo=promo),
        parse_mode=HTML,
    )


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
            fmt(get_msg(lang, "claim_already"), code=already), parse_mode=HTML
        )
        return

    count = sheets.get_invite_count(user_id)
    promo_name = get_promo_for_count(count)

    if not promo_name:
        await update.message.reply_text(get_msg(lang, "claim_not_eligible"), parse_mode=HTML)
        return

    promo_code = promo_name  # ← replace with real codes in config.py
    sheets.save_claim(user_id, username, promo_name, promo_code)

    await update.message.reply_text(
        fmt(get_msg(lang, "claim_eligible"), first_name=first_name,
            promo=promo_name, code=promo_code),
        parse_mode=HTML,
    )
    logger.info(f"{username} ({user_id}) claimed {promo_name}")


# ─── /help ───────────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = sheets.get_user_language(update.effective_user.id) or "en"
    await update.message.reply_text(get_msg(lang, "help"), parse_mode=HTML)


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

    invited_user = result.new_chat_member.user
    invited_user_id = invited_user.id
    invited_username = invited_user.username or invited_user.first_name or "unknown"
    invited_full_name = f"{invited_user.first_name or ''} {invited_user.last_name or ''}".strip() or invited_username
    link_url = invite_link_obj.invite_link

    owner_id = sheets.get_link_owner(link_url)
    if not owner_id:
        return

    # ── Fraud: self-invite ────────────────────────────────────────────────────
    if invited_user_id == owner_id:
        logger.warning(f"Self-invite blocked: {invited_user_id}")
        return

    # ── Fraud: rejoin (already counted before) ────────────────────────────────
    if sheets.has_already_joined(invited_user_id, owner_id):
        logger.warning(f"Rejoin blocked: {invited_user_id} already counted for {owner_id}")
        return

    # ── Fraud: new account age check ──────────────────────────────────────────
    if CHECK_ACCOUNT_AGE:
        # Record first seen so we have an exact timestamp going forward
        sheets.record_first_seen(invited_user_id)

        if is_account_too_new(invited_user_id):
            logger.warning(
                f"New account blocked: {invited_user_id} ({invited_username}) "
                f"is younger than {MIN_ACCOUNT_AGE_HOURS}h. Invited by {owner_id}."
            )
            # Notify the inviter in their language
            inviter_lang = sheets.get_user_language(owner_id) or "en"
            try:
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=fmt(
                        get_msg(inviter_lang, "new_account_blocked"),
                        username=invited_username,
                        hours=MIN_ACCOUNT_AGE_HOURS,
                    ),
                    parse_mode=HTML,
                )
            except Exception as e:
                logger.warning(f"Could not notify inviter {owner_id}: {e}")
            return

    # ── Valid join ────────────────────────────────────────────────────────────
    sheets.record_join(
        invited_user_id=invited_user_id,
        invited_username=invited_username,
        invited_full_name=invited_full_name,
        inviter_user_id=owner_id,
        invite_link=link_url,
    )
    new_count = sheets.increment_invite_count(owner_id)
    logger.info(f"Valid join recorded. Inviter {owner_id} now has {new_count} invites.")

    # Notify inviter if they hit a new reward threshold
    thresholds = {t[0] for t in PROMO_TIERS}
    if new_count in thresholds:
        lang = sheets.get_user_language(owner_id) or "en"
        promo = get_promo_for_count(new_count)
        try:
            await context.bot.send_message(
                chat_id=owner_id,
                text=fmt(get_msg(lang, "threshold_reached"),
                         promo=promo, deadline=CLAIM_DEADLINE),
                parse_mode=HTML,
            )
        except Exception as e:
            logger.warning(f"Could not notify {owner_id}: {e}")


# ─── Admin ────────────────────────────────────────────────────────────────────

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        members = sheets.get_worksheet("Members").get_all_values()
        claims  = sheets.get_worksheet("Claims").get_all_values()
        joins   = sheets.get_worksheet("Joins").get_all_values()
        active  = sheets.count_active_inviters()

        limit_text = f"{MAX_INVITERS}" if MAX_INVITERS > 0 else "Unlimited"

        await update.message.reply_text(
            f"📊 <b>Admin Stats</b>\n\n"
            f"👥 Total members: <b>{max(0, len(members)-1)}</b>\n"
            f"🔗 Active inviters: <b>{active}</b> / {limit_text}\n"
            f"📥 Total joins logged: <b>{max(0, len(joins)-1)}</b>\n"
            f"🎁 Total claims: <b>{max(0, len(claims)-1)}</b>\n\n"
            f"🟢 Campaign active: <b>{'Yes' if CAMPAIGN_ACTIVE else 'No'}</b>",
            parse_mode=HTML,
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def admin_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/reset — asks admin to confirm before wiping everything."""
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "⚠️ <b>WARNING — Full Reset</b>\n\n"
        "This will permanently delete <b>ALL</b> data:\n"
        "• All members &amp; invite links\n"
        "• All join records\n"
        "• All claims\n"
        "• All stats\n"
        "• All first-seen records\n\n"
        "To confirm, send /resetconfirm\n"
        "To cancel, just ignore this message.",
        parse_mode=HTML,
    )


async def admin_reset_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/resetconfirm — actually performs the reset."""
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("🔄 Resetting all data, please wait...")

    try:
        sheets.reset_all_data()
        logger.info(f"Full reset performed by admin {ADMIN_ID}")
        await update.message.reply_text(
            "✅ <b>Reset complete!</b>\n\n"
            "All sheets have been wiped and are ready for a new campaign.\n\n"
            "• Members → cleared\n"
            "• Joins → cleared\n"
            "• Claims → cleared\n"
            "• Stats → cleared\n"
            "• FirstSeen → cleared",
            parse_mode=HTML,
        )
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        await update.message.reply_text(f"❌ Reset failed: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    logger.info(f"Starting bot (python-telegram-bot {telegram.__version__})")
    logger.info(
        f"Campaign active: {CAMPAIGN_ACTIVE} | Max inviters: {MAX_INVITERS} | "
        f"Photo check: {CHECK_PROFILE_PHOTO} | Account age check: {CHECK_ACCOUNT_AGE} "
        f"(min {MIN_ACCOUNT_AGE_HOURS}h)"
    )

    try:
        sheets.setup_sheets()
        logger.info("Sheets ready.")
    except Exception as e:
        logger.error(f"Sheets init failed: {e}")
        raise

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("claim", claim_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("adminstats", admin_stats))
    app.add_handler(CommandHandler("reset", admin_reset))
    app.add_handler(CommandHandler("resetconfirm", admin_reset_confirm))
    app.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(ChatMemberHandler(track_new_member, ChatMemberHandler.CHAT_MEMBER))

    logger.info("Bot polling started.")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
