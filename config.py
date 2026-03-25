# ============================================================
#  config.py — Edit this file to update bot settings
#  Then push to GitHub — Railway redeploys in ~30 seconds
# ============================================================

# ─── TEST MODE ───────────────────────────────────────────────
# True  → all languages go to the test channel
# False → each language goes to its own real channel
TEST_MODE = True
TEST_CHANNEL_ID = -1002916936846  # ← your test channel ID

# ─── CAMPAIGN STATUS ─────────────────────────────────────────
# True  → campaign is running normally
# False → bot tells everyone the campaign has ended
CAMPAIGN_ACTIVE = True

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
    "mx": -1003389432490,
}


def get_channel(lang: str) -> int:
    """Returns the correct channel ID based on TEST_MODE."""
    if TEST_MODE:
        return TEST_CHANNEL_ID
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
CLAIM_DEADLINE = "April 30, 2026"
BRAND_NAME = "Rolletto"  # ← change to your brand name
