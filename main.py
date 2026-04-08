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
    CHECK_ACCOUNT_AGE, MIN_ACCOUNT_AGE_HOURS, INVITE_HOLD_HOURS,
    ACTIVE_LANG, get_channel,
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

# ─── Language button labels ───────────────────────────────────────────────────
LANG_BUTTONS = {
    "en": "🇬🇧 English",
    "it": "🇮🇹 Italiano",
    "fr": "🇫🇷 Français",
    "mx": "🇲🇽 Español",
}


# ─── ACTIVE_LANG mode helpers ─────────────────────────────────────────────────

def get_active_langs() -> list[str]:
    if ACTIVE_LANG == "all":
        return ["en", "it", "fr", "mx"]
    if isinstance(ACTIVE_LANG, list):
        return list(ACTIVE_LANG)
    return [ACTIVE_LANG]


def is_single_lang() -> bool:
    return len(get_active_langs()) == 1


def get_forced_lang() -> str | None:
    if is_single_lang():
        return get_active_langs()[0]
    return None


# ─── Core helpers ─────────────────────────────────────────────────────────────

def get_promo_for_count(count: int) -> tuple[str, str] | None:
    """
    Returns (tier_display_name, promo_code) for the highest unlocked tier,
    or None if the user hasn't reached any tier yet.
    """
    current = None
    for min_count, tier_name, promo_code in PROMO_TIERS:
        if count >= min_count:
            current = (tier_name, promo_code)
    return current


def get_msg(lang: str, key: str) -> str:
    return MESSAGES.get(lang, MESSAGES["en"]).get(key, "")


def fmt(template: str, **kwargs) -> str:
    safe = {k: (v if k == "link" else escape(str(v))) for k, v in kwargs.items()}
    return template.format(**safe)


def build_language_picker() -> InlineKeyboardMarkup:
    active = get_active_langs()
    buttons = [
        InlineKeyboardButton(LANG_BUTTONS[l], callback_data=f"lang_{l}")
        for l in active
    ]
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(keyboard)


def build_multi_lang_greeting() -> str:
    active = get_active_langs()
    parts = [get_msg(lang, "select_language_prompt") for lang in active]
    return "\n\n".join(parts)


async def has_profile_photo(bot, user_id: int) -> bool:
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        return photos.total_count > 0
    except Exception as e:
        logger.warning(f"Could not check profile photo for {user_id}: {e}")
        return True  # fail open


def estimate_account_age_hours(user_id: int) -> float:
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
    return (datetime.utcnow() - estimated_date).total_seconds() / 3600


def is_account_too_new(user_id: int) -> bool:
    if estimate_account_age_hours(user_id) >= MIN_ACCOUNT_AGE_HOURS:
        return False
    first_seen = sheets.get_first_seen(user_id)
    if first_seen is None:
        sheets.record_first_seen(user_id)
        return True
    return (datetime.utcnow() - first_seen).total_seconds() / 3600 < MIN_ACCOUNT_AGE_HOURS


# ─── /start ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    sheets.record_first_seen(user.id)

    # ── Mark bot_started in Pending if this user was invited ─────────────────
    # This is the proof that the invited user actually engaged with the bot
    sheets.mark_bot_started(user.id)

    # ── Campaign ended ────────────────────────────────────────────────────────
    if not CAMPAIGN_ACTIVE:
        lang = get_forced_lang() or sheets.get_user_language(user.id) or "en"
        await update.message.reply_text(get_msg(lang, "campaign_ended"), parse_mode=HTML)
        return

    # ── MODE 3: Single language — no picker ───────────────────────────────────
    if is_single_lang():
        lang = get_forced_lang()
        sheets.set_user_language(user.id, lang)
        await update.message.reply_text(get_msg(lang, "welcome_single"), parse_mode=HTML)
        return

    # ── MODE 1 & 2: Language picker ───────────────────────────────────────────
    greeting = build_multi_lang_greeting()
    await update.message.reply_text(
        greeting,
        reply_markup=build_language_picker(),
        parse_mode=HTML,
    )


# ─── Language selection callback ─────────────────────────────────────────────

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]

    if lang not in get_active_langs():
        await query.answer("This language is not available.", show_alert=True)
        return

    sheets.set_user_language(query.from_user.id, lang)
    await query.edit_message_text(get_msg(lang, "language_set"), parse_mode=HTML)


# Trigger words per language (with and without quotes)
INVITE_TRIGGER_WORDS = {
    "en": ("invite",   '"invite"'),
    "it": ("invita",   '"invita"'),
    "fr": ("inviter",  '"inviter"'),
    "mx": ("invitar",  '"invitar"'),
}
ALL_INVITE_TRIGGERS = {w for words in INVITE_TRIGGER_WORDS.values() for w in words}


# ─── "invite" keyword ────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if update.message.text.strip().lower() not in ALL_INVITE_TRIGGERS:
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or "user"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or username
    first_name = user.first_name or "there"

    sheets.record_first_seen(user_id)

    # ── Resolve language ──────────────────────────────────────────────────────
    if is_single_lang():
        lang = get_forced_lang()
        sheets.set_user_language(user_id, lang)
    else:
        lang = sheets.get_user_language(user_id)
        if not lang:
            await update.message.reply_text(
                "👋 Please select your language first using /start", parse_mode=HTML
            )
            return

    # ── Campaign ended ────────────────────────────────────────────────────────
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
            await update.message.reply_text(get_msg(lang, "campaign_full"), parse_mode=HTML)
            logger.info(f"Max inviters reached ({MAX_INVITERS}). Blocked {username} ({user_id})")
            return

    # ── Alt account check ─────────────────────────────────────────────────────
    if CHECK_PROFILE_PHOTO:
        has_photo = await has_profile_photo(context.bot, user_id)
        if not has_photo:
            await update.message.reply_text(get_msg(lang, "alt_account_blocked"), parse_mode=HTML)
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
            get_msg(lang, "invite_link_failed"), parse_mode=HTML
        )


# ─── Inactivity jobs ─────────────────────────────────────────────────────────

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


# ─── Pending confirmation job (runs every hour) ───────────────────────────────

async def process_pending_joins(context: ContextTypes.DEFAULT_TYPE):
    """
    Runs every hour. Checks all pending joins whose hold period has expired.
    For each one:
      - If bot_started=True AND still in channel → confirm, count, notify inviter
      - Otherwise → discard silently
    Rows are deleted after processing (in reverse order to avoid row shifting).
    """
    ready = sheets.get_ready_pending(INVITE_HOLD_HOURS)
    if not ready:
        logger.info("process_pending_joins: nothing ready.")
        return

    logger.info(f"process_pending_joins: processing {len(ready)} expired pending rows.")

    for entry in ready:  # already sorted descending by row_num
        invited_user_id  = entry["invited_user_id"]
        inviter_user_id  = entry["inviter_user_id"]
        channel_id       = entry["channel_id"]
        confirmed        = False

        if entry["bot_started"]:
            # Check if the invited user is still in the channel
            try:
                member = await context.bot.get_chat_member(
                    chat_id=channel_id,
                    user_id=invited_user_id,
                )
                if member.status in ("member", "administrator", "creator"):
                    confirmed = True
                else:
                    logger.info(
                        f"Pending discarded: {invited_user_id} left the channel "
                        f"(status={member.status})"
                    )
            except Exception as e:
                # Can't check membership — skip this row for now, retry next hour
                logger.warning(
                    f"Could not check membership for {invited_user_id}: {e} — skipping."
                )
                continue
        else:
            logger.info(
                f"Pending discarded: {invited_user_id} never started the bot."
            )

        # Remove from Pending sheet
        try:
            sheets.remove_pending_row(entry["row_num"])
        except Exception as e:
            logger.warning(f"Could not remove pending row {entry['row_num']}: {e}")
            continue

        if confirmed:
            # Move to Joins and credit the inviter
            sheets.record_join(
                invited_user_id=invited_user_id,
                invited_username=entry["invited_username"],
                invited_full_name=entry["invited_full_name"],
                inviter_user_id=inviter_user_id,
                invite_link=entry["invite_link"],
            )
            new_count = sheets.increment_invite_count(inviter_user_id)
            logger.info(
                f"Invite confirmed: {invited_user_id} → inviter {inviter_user_id}, "
                f"new count: {new_count}"
            )

            # Notify inviter of tier unlock if threshold hit
            thresholds = {t[0] for t in PROMO_TIERS}
            if new_count in thresholds:
                lang = get_forced_lang() or sheets.get_user_language(inviter_user_id) or "en"
                tier_result = get_promo_for_count(new_count)
                if tier_result:
                    tier_name, _ = tier_result
                    try:
                        await context.bot.send_message(
                            chat_id=inviter_user_id,
                            text=fmt(
                                get_msg(lang, "threshold_reached"),
                                promo=tier_name,
                                deadline=CLAIM_DEADLINE,
                            ),
                            parse_mode=HTML,
                        )
                    except Exception as e:
                        logger.warning(f"Could not notify inviter {inviter_user_id}: {e}")


# ─── /status ─────────────────────────────────────────────────────────────────

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "there"
    lang = get_forced_lang() or sheets.get_user_language(user_id) or "en"

    if not sheets.get_user_invite_link(user_id):
        await update.message.reply_text(get_msg(lang, "status_no_link"), parse_mode=HTML)
        return

    count = sheets.get_invite_count(user_id)
    result = get_promo_for_count(count)
    promo_display = result[0] if result else "—"

    await update.message.reply_text(
        fmt(get_msg(lang, "status"), first_name=first_name, count=count, promo=promo_display),
        parse_mode=HTML,
    )


# ─── /claim ──────────────────────────────────────────────────────────────────

async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or "user"
    first_name = user.first_name or "there"
    lang = get_forced_lang() or sheets.get_user_language(user_id) or "en"

    already = sheets.get_claimed_promo(user_id)
    if already:
        await update.message.reply_text(
            fmt(get_msg(lang, "claim_already"), code=already), parse_mode=HTML
        )
        return

    count = sheets.get_invite_count(user_id)
    result = get_promo_for_count(count)

    if not result:
        await update.message.reply_text(get_msg(lang, "claim_not_eligible"), parse_mode=HTML)
        return

    tier_name, promo_code = result
    sheets.save_claim(user_id, username, tier_name, promo_code)

    await update.message.reply_text(
        fmt(get_msg(lang, "claim_eligible"), first_name=first_name,
            promo=tier_name, code=promo_code),
        parse_mode=HTML,
    )
    logger.info(f"{username} ({user_id}) claimed tier '{tier_name}' → code '{promo_code}'")


# ─── /help ───────────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_forced_lang() or sheets.get_user_language(update.effective_user.id) or "en"
    await update.message.reply_text(get_msg(lang, "help"), parse_mode=HTML)


# ─── Channel join tracker ─────────────────────────────────────────────────────

async def track_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    joined     = result.new_chat_member.status in ("member", "administrator", "creator")
    was_outside = result.old_chat_member.status in ("left", "kicked", "restricted")

    if not (joined and was_outside):
        return

    invite_link_obj = result.invite_link
    if not invite_link_obj:
        return

    invited_user      = result.new_chat_member.user
    invited_user_id   = invited_user.id
    invited_username  = invited_user.username or invited_user.first_name or "unknown"
    invited_full_name = (
        f"{invited_user.first_name or ''} {invited_user.last_name or ''}".strip()
        or invited_username
    )
    link_url   = invite_link_obj.invite_link
    channel_id = result.chat.id

    owner_id = sheets.get_link_owner(link_url)
    if not owner_id:
        return

    # ── Fraud: self-invite ────────────────────────────────────────────────────
    if invited_user_id == owner_id:
        logger.warning(f"Self-invite blocked: {invited_user_id}")
        return

    # ── Fraud: already joined or already pending ──────────────────────────────
    if sheets.has_already_joined(invited_user_id, owner_id):
        logger.warning(
            f"Duplicate blocked: {invited_user_id} already in Joins or Pending for {owner_id}"
        )
        return

    # ── Fraud: new account age ────────────────────────────────────────────────
    if CHECK_ACCOUNT_AGE:
        sheets.record_first_seen(invited_user_id)
        if is_account_too_new(invited_user_id):
            logger.warning(
                f"New account blocked: {invited_user_id} ({invited_username}) "
                f"younger than {MIN_ACCOUNT_AGE_HOURS}h. Invited by {owner_id}."
            )
            inviter_lang = get_forced_lang() or sheets.get_user_language(owner_id) or "en"
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

    # ── Save to Pending (hold period starts now) ──────────────────────────────
    # Check if this is the inviter's very first pending join
    pending_before = sheets.count_pending_for_inviter(owner_id)

    sheets.save_pending_join(
        invited_user_id=invited_user_id,
        invited_username=invited_username,
        invited_full_name=invited_full_name,
        inviter_user_id=owner_id,
        invite_link=link_url,
        channel_id=channel_id,
    )
    logger.info(
        f"Join saved to Pending: {invited_user_id} invited by {owner_id}. "
        f"Will confirm in {INVITE_HOLD_HOURS}h if they start the bot and stay."
    )

    # ── First pending join: remind inviter of the rules ───────────────────────
    if pending_before == 0:
        inviter_lang = get_forced_lang() or sheets.get_user_language(owner_id) or "en"
        try:
            await context.bot.send_message(
                chat_id=owner_id,
                text=get_msg(inviter_lang, "first_join_reminder"),
                parse_mode=HTML,
            )
        except Exception as e:
            logger.warning(f"Could not send first_join_reminder to {owner_id}: {e}")


# ─── Admin ────────────────────────────────────────────────────────────────────

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        members = sheets.get_worksheet("Members").get_all_values()
        claims  = sheets.get_worksheet("Claims").get_all_values()
        joins   = sheets.get_worksheet("Joins").get_all_values()
        pending = sheets.get_worksheet("Pending").get_all_values()
        active  = sheets.count_active_inviters()
        limit_text = f"{MAX_INVITERS}" if MAX_INVITERS > 0 else "Unlimited"

        await update.message.reply_text(
            f"📊 <b>Admin Stats</b>\n\n"
            f"👥 Total members: <b>{max(0, len(members)-1)}</b>\n"
            f"🔗 Active inviters: <b>{active}</b> / {limit_text}\n"
            f"📥 Confirmed joins: <b>{max(0, len(joins)-1)}</b>\n"
            f"⏳ Pending joins: <b>{max(0, len(pending)-1)}</b>\n"
            f"🎁 Total claims: <b>{max(0, len(claims)-1)}</b>\n\n"
            f"🟢 Campaign active: <b>{'Yes' if CAMPAIGN_ACTIVE else 'No'}</b>\n"
            f"🌍 Active language(s): <b>{ACTIVE_LANG}</b>\n"
            f"⏰ Hold period: <b>{INVITE_HOLD_HOURS}h</b>",
            parse_mode=HTML,
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def admin_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "⚠️ <b>WARNING — Full Reset</b>\n\n"
        "This will permanently delete <b>ALL</b> data:\n"
        "• All members &amp; invite links\n"
        "• All join records\n"
        "• All pending joins\n"
        "• All claims\n"
        "• All stats\n"
        "• All first-seen records\n\n"
        "To confirm, send /resetconfirm\n"
        "To cancel, just ignore this message.",
        parse_mode=HTML,
    )


async def admin_reset_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            "• Pending → cleared\n"
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
        f"Campaign active: {CAMPAIGN_ACTIVE} | Active lang: {ACTIVE_LANG} | "
        f"Max inviters: {MAX_INVITERS} | Photo check: {CHECK_PROFILE_PHOTO} | "
        f"Account age check: {CHECK_ACCOUNT_AGE} (min {MIN_ACCOUNT_AGE_HOURS}h) | "
        f"Invite hold: {INVITE_HOLD_HOURS}h"
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

    # ── Hourly job: confirm or discard pending joins ──────────────────────────
    app.job_queue.run_repeating(
        process_pending_joins,
        interval=3600,   # every hour
        first=60,        # first run 60 seconds after startup
        name="pending_confirmation",
    )

    logger.info("Bot polling started.")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
