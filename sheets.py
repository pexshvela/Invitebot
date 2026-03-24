# ============================================================
#  sheets.py — All Google Sheets read/write operations
# ============================================================

import os
import json
import logging
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Cached connection
_spreadsheet = None


def get_spreadsheet():
    global _spreadsheet
    if _spreadsheet is None:
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        _spreadsheet = client.open_by_key(sheet_id)
    return _spreadsheet


def get_worksheet(name: str):
    """Get a worksheet by name, creating it if it doesn't exist."""
    ss = get_spreadsheet()
    try:
        return ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=2000, cols=20)
        return ws


def setup_sheets():
    """Initialize all required sheets with headers on first run."""
    members_ws = get_worksheet("Members")
    if not members_ws.get_all_values():
        members_ws.append_row(
            ["user_id", "username", "full_name", "language", "invite_link", "date_joined", "invite_count"]
        )
        logger.info("Members sheet initialized.")

    claims_ws = get_worksheet("Claims")
    if not claims_ws.get_all_values():
        claims_ws.append_row(
            ["user_id", "username", "promo_name", "promo_code", "date_claimed"]
        )
        logger.info("Claims sheet initialized.")

    stats_ws = get_worksheet("Stats")
    if not stats_ws.get_all_values():
        stats_ws.append_row(
            ["user_id", "username", "language", "invite_count", "last_updated"]
        )
        logger.info("Stats sheet initialized.")

    config_ws = get_worksheet("Config")
    if not config_ws.get_all_values():
        config_ws.append_row(["key", "value"])
        config_ws.append_row(["claim_deadline", "April 30, 2026"])
        config_ws.append_row(["promo1", "PROMO1"])
        config_ws.append_row(["promo2", "PROMO2"])
        config_ws.append_row(["promo3", "PROMO3"])
        config_ws.append_row(["promo4", "PROMO4"])
        config_ws.append_row(["promo5", "PROMO5"])
        config_ws.append_row(["promo6", "PROMO6"])
        logger.info("Config sheet initialized.")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _find_member_row(user_id: int):
    """Find the row of a member. Returns (worksheet, row_index) or (ws, None)."""
    ws = get_worksheet("Members")
    try:
        cell = ws.find(str(user_id), in_column=1)
        return ws, cell.row
    except gspread.exceptions.CellNotFound:
        return ws, None


# ─── Language ─────────────────────────────────────────────────────────────────

def get_user_language(user_id: int) -> str | None:
    ws, row = _find_member_row(user_id)
    if row is None:
        return None
    return ws.cell(row, 4).value or None  # col D = language


def set_user_language(user_id: int, lang: str):
    ws, row = _find_member_row(user_id)
    if row is None:
        # Create a partial record — will be filled in when they send "invite"
        ws.append_row([str(user_id), "", "", lang, "", "", 0])
    else:
        ws.update_cell(row, 4, lang)


# ─── Invite Link ──────────────────────────────────────────────────────────────

def get_user_invite_link(user_id: int) -> str | None:
    ws, row = _find_member_row(user_id)
    if row is None:
        return None
    link = ws.cell(row, 5).value  # col E = invite_link
    return link if link else None


def save_member(
    user_id: int,
    username: str,
    full_name: str,
    lang: str,
    invite_link: str,
):
    ws, row = _find_member_row(user_id)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if row is None:
        ws.append_row([str(user_id), username, full_name, lang, invite_link, now, 0])
    else:
        existing_count = ws.cell(row, 7).value or 0
        ws.update(
            f"B{row}:G{row}",
            [[username, full_name, lang, invite_link, now, existing_count]],
        )


# ─── Invite Tracking ─────────────────────────────────────────────────────────

def get_link_owner(link_url: str) -> int | None:
    """Return user_id of whoever owns this invite link."""
    ws = get_worksheet("Members")
    try:
        cell = ws.find(link_url, in_column=5)
        return int(ws.cell(cell.row, 1).value)
    except (gspread.exceptions.CellNotFound, ValueError, TypeError):
        return None


def get_invite_count(user_id: int) -> int:
    ws, row = _find_member_row(user_id)
    if row is None:
        return 0
    try:
        return int(ws.cell(row, 7).value or 0)  # col G = invite_count
    except (ValueError, TypeError):
        return 0


def increment_invite_count(user_id: int) -> int:
    """Increment invite count and return the new value."""
    ws, row = _find_member_row(user_id)
    if row is None:
        return 0
    current = get_invite_count(user_id)
    new_count = current + 1
    ws.update_cell(row, 7, new_count)

    # Also update Stats sheet
    _update_stats(user_id, ws.cell(row, 2).value, ws.cell(row, 4).value, new_count)
    return new_count


def _update_stats(user_id: int, username: str, lang: str, count: int):
    ws = get_worksheet("Stats")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cell = ws.find(str(user_id), in_column=1)
        ws.update(f"A{cell.row}:E{cell.row}", [[str(user_id), username, lang, count, now]])
    except gspread.exceptions.CellNotFound:
        ws.append_row([str(user_id), username, lang, count, now])


# ─── Claims ───────────────────────────────────────────────────────────────────

def get_claimed_promo(user_id: int) -> str | None:
    """Return the promo code already claimed by user, or None."""
    ws = get_worksheet("Claims")
    try:
        cell = ws.find(str(user_id), in_column=1)
        return ws.cell(cell.row, 4).value  # col D = promo_code
    except gspread.exceptions.CellNotFound:
        return None


def save_claim(user_id: int, username: str, promo_name: str, promo_code: str):
    ws = get_worksheet("Claims")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([str(user_id), username, promo_name, promo_code, now])


def remove_invite_link(user_id: int):
    """Clear the invite link for a user (inactivity deletion)."""
    ws, row = _find_member_row(user_id)
    if row is None:
        return
    ws.update_cell(row, 5, "")  # col E = invite_link

