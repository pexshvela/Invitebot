# ============================================================
#  sheets.py — Google Sheets backend (gspread 6+ compatible)
#
#  KEY FIX: In gspread 6+, ws.find() returns None when not found
#  instead of raising CellNotFound. All lookups handle None.
# ============================================================

import os
import json
import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_spreadsheet = None


# ─── Connection ──────────────────────────────────────────────────────────────

def get_spreadsheet():
    global _spreadsheet
    if _spreadsheet is None:
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not creds_json:
            raise ValueError("Missing GOOGLE_CREDENTIALS_JSON env var")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        logger.info(f"Connecting to sheet: {sheet_id}")
        _spreadsheet = client.open_by_key(sheet_id)
        logger.info("Connected to Google Sheets.")
    return _spreadsheet


def get_worksheet(name: str):
    """Get worksheet by name, creating it if needed."""
    ss = get_spreadsheet()
    try:
        return ss.worksheet(name)
    except gspread.WorksheetNotFound:
        logger.info(f"Creating worksheet: {name}")
        return ss.add_worksheet(title=name, rows=5000, cols=20)


def setup_sheets():
    """
    Creates all required tabs with headers if they don't exist.
    Safe to call on every startup — only adds headers to empty sheets.
    """
    tabs = {
        "Members":   ["user_id", "username", "full_name", "language",
                      "invite_link", "date_joined", "invite_count"],
        "Joins":     ["invited_user_id", "invited_username", "invited_full_name",
                      "inviter_user_id", "invite_link", "joined_at"],
        "Claims":    ["user_id", "username", "promo_name", "promo_code", "date_claimed"],
        "Stats":     ["user_id", "username", "language", "invite_count", "last_updated"],
        "FirstSeen": ["user_id", "first_seen_at"],
    }
    for tab_name, headers in tabs.items():
        ws = get_worksheet(tab_name)
        existing = ws.get_all_values()
        if not existing:
            ws.append_row(headers)
            logger.info(f"Initialized tab: {tab_name}")
        else:
            logger.info(f"Tab '{tab_name}' already has data ({len(existing)} rows).")

    logger.info("All sheets ready.")


# ─── Safe find helper ─────────────────────────────────────────────────────────

def _find_cell(ws, value: str, in_column: int):
    """
    gspread 6+ compatible find. Returns the cell or None.
    Never raises CellNotFound.
    """
    try:
        return ws.find(value, in_column=in_column)
    except Exception:
        return None


# ─── Members ─────────────────────────────────────────────────────────────────

def _get_member_row(user_id: int):
    """Returns (worksheet, row_number) or (worksheet, None) if not found."""
    ws = get_worksheet("Members")
    cell = _find_cell(ws, str(user_id), in_column=1)
    if cell is None:
        return ws, None
    return ws, cell.row


def get_user_language(user_id: int) -> str | None:
    ws, row = _get_member_row(user_id)
    if row is None:
        return None
    val = ws.cell(row, 4).value
    return val if val else None


def set_user_language(user_id: int, lang: str):
    ws, row = _get_member_row(user_id)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if row is None:
        ws.append_row([str(user_id), "", "", lang, "", now, 0])
    else:
        ws.update_cell(row, 4, lang)


def get_user_invite_link(user_id: int) -> str | None:
    ws, row = _get_member_row(user_id)
    if row is None:
        return None
    val = ws.cell(row, 5).value
    return val if val else None


def save_member(user_id: int, username: str, full_name: str, lang: str, invite_link: str):
    ws, row = _get_member_row(user_id)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if row is None:
        ws.append_row([str(user_id), username, full_name, lang, invite_link, now, 0])
    else:
        existing_count = ws.cell(row, 7).value or 0
        ws.update(f"B{row}:G{row}", [[username, full_name, lang, invite_link, now, existing_count]])


def remove_invite_link(user_id: int):
    ws, row = _get_member_row(user_id)
    if row is None:
        return
    ws.update_cell(row, 5, "")
    ws.update_cell(row, 7, 0)


def get_link_owner(link_url: str) -> int | None:
    ws = get_worksheet("Members")
    cell = _find_cell(ws, link_url, in_column=5)
    if cell is None:
        return None
    try:
        return int(ws.cell(cell.row, 1).value)
    except (ValueError, TypeError):
        return None


def count_active_inviters() -> int:
    """Count members who have a non-empty invite link."""
    ws = get_worksheet("Members")
    rows = ws.get_all_values()
    if len(rows) <= 1:
        return 0
    return sum(1 for row in rows[1:] if len(row) >= 5 and row[4].strip())


# ─── Invite counts ───────────────────────────────────────────────────────────

def get_invite_count(user_id: int) -> int:
    ws, row = _get_member_row(user_id)
    if row is None:
        return 0
    try:
        return int(ws.cell(row, 7).value or 0)
    except (ValueError, TypeError):
        return 0


def increment_invite_count(user_id: int) -> int:
    ws, row = _get_member_row(user_id)
    if row is None:
        return 0
    new_count = get_invite_count(user_id) + 1
    ws.update_cell(row, 7, new_count)

    # Mirror to Stats tab
    try:
        username = ws.cell(row, 2).value or ""
        lang = ws.cell(row, 4).value or ""
        stats_ws = get_worksheet("Stats")
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        c = _find_cell(stats_ws, str(user_id), in_column=1)
        if c:
            stats_ws.update(f"A{c.row}:E{c.row}", [[str(user_id), username, lang, new_count, now]])
        else:
            stats_ws.append_row([str(user_id), username, lang, new_count, now])
    except Exception as e:
        logger.warning(f"Stats update failed: {e}")

    return new_count


# ─── Joins (fraud prevention) ─────────────────────────────────────────────────

def has_already_joined(invited_user_id: int, inviter_user_id: int) -> bool:
    """Returns True if this (invited, inviter) pair already exists — blocks rejoin fraud."""
    ws = get_worksheet("Joins")
    try:
        all_rows = ws.get_all_values()
        for row in all_rows[1:]:  # skip header
            if len(row) >= 4 and row[0] == str(invited_user_id) and row[3] == str(inviter_user_id):
                return True
    except Exception as e:
        logger.warning(f"has_already_joined check failed: {e}")
    return False


def record_join(invited_user_id: int, invited_username: str, invited_full_name: str,
                inviter_user_id: int, invite_link: str):
    """Log a valid new join."""
    ws = get_worksheet("Joins")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([str(invited_user_id), invited_username, invited_full_name,
                   str(inviter_user_id), invite_link, now])


# ─── First Seen (account age fraud prevention) ───────────────────────────────

def record_first_seen(user_id: int):
    """
    Records the first time this user_id is seen by the bot.
    Safe to call multiple times — only writes on the very first call.
    """
    ws = get_worksheet("FirstSeen")
    cell = _find_cell(ws, str(user_id), in_column=1)
    if cell is None:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([str(user_id), now])
        logger.info(f"First seen recorded for user {user_id}")


def get_first_seen(user_id: int) -> datetime | None:
    """
    Returns the datetime when this user_id was first seen, or None if unknown.
    """
    ws = get_worksheet("FirstSeen")
    cell = _find_cell(ws, str(user_id), in_column=1)
    if cell is None:
        return None
    try:
        val = ws.cell(cell.row, 2).value
        if val:
            return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.warning(f"get_first_seen parse failed for {user_id}: {e}")
    return None


# ─── Claims ──────────────────────────────────────────────────────────────────

def get_claimed_promo(user_id: int) -> str | None:
    ws = get_worksheet("Claims")
    cell = _find_cell(ws, str(user_id), in_column=1)
    if cell is None:
        return None
    return ws.cell(cell.row, 4).value  # col D = promo_code


def save_claim(user_id: int, username: str, promo_name: str, promo_code: str):
    ws = get_worksheet("Claims")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([str(user_id), username, promo_name, promo_code, now])


# ─── Full reset ───────────────────────────────────────────────────────────────

def reset_all_data():
    """Wipe all data sheets, keep headers. Used by /resetconfirm admin command."""
    headers = {
        "Members":   ["user_id", "username", "full_name", "language",
                      "invite_link", "date_joined", "invite_count"],
        "Joins":     ["invited_user_id", "invited_username", "invited_full_name",
                      "inviter_user_id", "invite_link", "joined_at"],
        "Claims":    ["user_id", "username", "promo_name", "promo_code", "date_claimed"],
        "Stats":     ["user_id", "username", "language", "invite_count", "last_updated"],
        "FirstSeen": ["user_id", "first_seen_at"],
    }
    for tab_name, header_row in headers.items():
        ws = get_worksheet(tab_name)
        ws.clear()
        ws.append_row(header_row)
        logger.info(f"Sheet '{tab_name}' reset.")
    logger.info("Full reset complete.")
