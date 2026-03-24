# ============================================================
#  config.py — Edit this file to update bot settings
#  Then redeploy on Railway (takes ~30 seconds)
# ============================================================

# --- TEST MODE ---
# Set TEST_MODE = True to route ALL languages to the test channel
# Set TEST_MODE = False when you're ready to go live with all 4 channels
TEST_MODE = True
TEST_CHANNEL_ID = -1001002961190744  # ← your test channel

# --- Channel IDs per language (used when TEST_MODE = False) ---
CHANNELS = {
    "en": -1002326259934,
    "it": -1003220500138,
    "fr": -1003471986771,
    "mx": -1003389432490,
}


def get_channel(lang: str) -> int:
    """Returns the correct channel based on TEST_MODE."""
    if TEST_MODE:
        return TEST_CHANNEL_ID
    return CHANNELS[lang]

# --- Promo tiers: (minimum_invites, promo_code_value) ---
# Update the promo code values (right side) with your real codes when ready
PROMO_TIERS = [
    (1,   "PROMO1"),
    (6,   "PROMO2"),
    (11,  "PROMO3"),
    (31,  "PROMO4"),
    (71,  "PROMO5"),
    (100, "PROMO6"),
]

# --- General settings ---
CLAIM_DEADLINE = "April 30, 2026"
BRAND_NAME = "YourBrand"   # ← Change this to your brand name
