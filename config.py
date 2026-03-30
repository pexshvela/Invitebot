# ============================================================
#  config.py — Edit this file to update bot settings
#  Then push to GitHub — Railway redeploys in ~30 seconds
# ============================================================

# ─── TEST MODE ───────────────────────────────────────────────
# True  → all languages go to the test channel
# False → each language goes to its own real channel
TEST_MODE = False
TEST_CHANNEL_ID = -1002916936846  # ← your test channel ID

# ─── CAMPAIGN STATUS ─────────────────────────────────────────
# True  → campaign is running normally
# False → bot tells everyone the campaign has ended
CAMPAIGN_ACTIVE = True

# ─── ACTIVE LANGUAGE / MARKET ────────────────────────────────
# Controls which language market(s) are active. Three options:
#
#   "all"          → all 4 languages active, user sees full 4-button picker
#
#   "mx"           → single market only (Spanish)
#                    no language picker shown, everything in Spanish
#                    same works for: "en", "it", "fr"
#
#   ["mx", "fr"]   → two or more specific markets at the same time
#                    user sees a reduced picker with only those language buttons
#                    greeting shown in all selected languages
#                    example with 3: ["en", "it", "mx"]
#
ACTIVE_LANG = "mx"

# ─── MAX INVITERS ────────────────────────────────────────────
# Maximum number of people who can get an invite link
# Once this limit is reached, new users will be told the campaign is full
# Set to 0 for unlimited
MAX_INVITERS = 0

# ─── ALT ACCOUNT PROTECTION ──────────────────────────────────
# True  → block accounts with no profile photo (likely fake/alt accounts)
# False → allow everyone regardless of profile photo
CHECK_PROFILE_PHOTO = False

# ─── NEW ACCOUNT AGE PROTECTION ──────────────────────────────
# True  → block accounts younger than MIN_ACCOUNT_AGE_HOURS
# False → allow accounts of any age
CHECK_ACCOUNT_AGE = True

# Minimum account age in hours required to count as a valid invite
# Accounts younger than this will be ignored and the inviter notified
MIN_ACCOUNT_AGE_HOURS = 24

# ─── Channel IDs per language (used when TEST_MODE = False) ──
CHANNELS = {
    "en": -1002326259934,
    "it": -1003220500138,
    "fr": -1003471986771,
    "mx": -1003637149020,
}


def get_active_langs() -> list:
    """Always returns the active language(s) as a list."""
    if ACTIVE_LANG == "all":
        return ["en", "it", "fr", "mx"]
    if isinstance(ACTIVE_LANG, list):
        return ACTIVE_LANG
    return [ACTIVE_LANG]  # single string like "mx"


def is_single_lang() -> bool:
    """True when exactly one language is active — no picker needed."""
    if ACTIVE_LANG == "all":
        return False
    if isinstance(ACTIVE_LANG, list):
        return len(ACTIVE_LANG) == 1
    return True  # plain string like "mx"


def get_forced_lang() -> str | None:
    """Returns the forced language code when is_single_lang() is True, else None."""
    if is_single_lang():
        return ACTIVE_LANG if isinstance(ACTIVE_LANG, str) else ACTIVE_LANG[0]
    return None


def get_channel(lang: str) -> int:
    """Returns the correct channel ID based on TEST_MODE and ACTIVE_LANG."""
    if TEST_MODE:
        return TEST_CHANNEL_ID
    if is_single_lang():
        return CHANNELS[get_forced_lang()]
    return CHANNELS[lang]


# ─── Promo tiers ─────────────────────────────────────────────
# Format: (minimum_invites, promo_code)
# Replace right side with real codes when ready
PROMO_TIERS = [
    (1,   "Tier1"),
    (6,   "Tier2"),
    (11,  "Tier3"),
    (31,  "Tier4"),
    (71,  "Tier5"),
    (100, "Tier6"),
]

# ─── General settings ────────────────────────────────────────
CLAIM_DEADLINE = "April 6, 2026"
BRAND_NAME = "Rolletto"  # ← change to your brand name
