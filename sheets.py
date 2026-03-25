# ============================================================
#  sheets.py — Google Sheets backend
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
    ss = get_spreadsheet()
    try:
        return ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=5000, cols=20)
        return ws


def setup_sheets():
    """Create all tabs with headers if they don't exist yet."""

    ws = get_worksheet("Members")
    if not ws.get_all_values():
        ws.append_row(["user_id", "username", "full_name", "language",
                       "invite_link", "date_joined", "invite_count"])

    ws = get_worksheet("Joins")
    if not ws.get_all_values():
        ws.append_row(["invited_user_id", "invited_username", "invited_full_name",
                       "inviter_user_id", "invite_link", "joined_at"])

    ws = get_worksheet("Claims")
    if not ws.get_all_values():
        ws.append_row(["user_id", "username", "promo_name", "promo_code", "date_claimed"])

    ws = get_worksheet("Stats")
    if not ws.get_all_values():
        ws.append_row(["user_id", "username", "language", "invite_count", "last_updated"])

    logger.info("All sheets ready.")


# ─── Language ────────────────────────────────────────────────────────────────

def _find_member_row(user_id: int):
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    if cell is None:
        return ws, None
    return ws, cell.row


def get_user_language(user_id: int) -> str | None:
    ws, row = _find_member_row(user_id)
    if row is None:
        return None
    return ws.cell(row, 4).value or None


def set_user_language(user_id: int, lang: str):
    ws, row = _find_member_row(user_id)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if row is None:
        ws.append_row([str(user_id), "", "", lang, "", now, 0])
    else:
        ws.update_cell(row, 4, lang)


# ─── Invite Link ─────────────────────────────────────────────────────────────

def get_user_invite_link(user_id: int) -> str | None:
    ws, row = _find_member_row(user_id)
    if row is None:
        return None
    val = ws.cell(row, 5).value
    return val if val else None


def save_member(user_id: int, username: str, full_name: str, lang: str, invite_link: str):
    ws, row = _find_member_row(user_id)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if row is None:
        ws.append_row([str(user_id), username, full_name, lang, invite_link, now, 0])
    else:
        ws.update(f"B{row}:G{row}", [[username, full_name, lang, invite_link, now,
                                      ws.cell(row, 7).value or 0]])


def remove_invite_link(user_id: int):
    ws, row = _find_member_row(user_id)
    if row is None:
        return
    ws.update_cell(row, 5, "")
    ws.update_cell(row, 7, 0)


def get_link_owner(link_url: str) -> int | None:
    ws = get_worksheet("Members")
    cell = ws.find(link_url, in_column=5)
    if cell is None:
        return None
    try:
        val = ws.cell(cell.row, 1).value
        return int(val) if val else None
    except (ValueError, TypeError):
        return None


# ─── Invite count ────────────────────────────────────────────────────────────

def get_invite_count(user_id: int) -> int:
    ws, row = _find_member_row(user_id)
    if row is None:
        return 0
    try:
        return int(ws.cell(row, 7).value or 0)
    except (ValueError, TypeError):
        return 0


def increment_invite_count(user_id: int) -> int:
    ws, row = _find_member_row(user_id)
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
        stats_cell = stats_ws.find(str(user_id), in_column=1)
        if stats_cell is None:
            stats_ws.append_row([str(user_id), username, lang, new_count, now])
        else:
            stats_ws.update(f"A{stats_cell.row}:E{stats_cell.row}",
                            [[str(user_id), username, lang, new_count, now]])
    except Exception as e:
        logger.warning(f"Stats update failed: {e}")

    return new_count


# ─── Max inviters check ──────────────────────────────────────────────────────

def count_active_inviters() -> int:
    """Count how many members have a non-empty invite link (= active inviters)."""
    ws = get_worksheet("Members")
    rows = ws.get_all_values()
    if not rows:
        return 0
    return sum(1 for row in rows[1:] if len(row) >= 5 and row[4].strip())


# ─── Joins / fraud prevention ────────────────────────────────────────────────

def has_already_joined(invited_user_id: int, inviter_user_id: int) -> bool:
    """
    Returns True if this exact (invited_user, inviter) pair is already in the Joins sheet.
    Blocks rejoin fraud: leaving and rejoining the channel won't count again.
    """
    ws = get_worksheet("Joins")
    try:
        cells = ws.findall(str(invited_user_id), in_column=1)
        for cell in cells:
            if ws.cell(cell.row, 4).value == str(inviter_user_id):
                return True
    except Exception as e:
        logger.warning(f"has_already_joined check failed: {e}")
    return False


def record_join(invited_user_id: int, invited_username: str, invited_full_name: str,
                inviter_user_id: int, invite_link: str):
    """Log a valid new join to the Joins sheet."""
    ws = get_worksheet("Joins")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([
        str(invited_user_id),
        invited_username,
        invited_full_name,
        str(inviter_user_id),
        invite_link,
        now,
    ])


# ─── Claims ──────────────────────────────────────────────────────────────────

def get_claimed_promo(user_id: int) -> str | None:
    ws = get_worksheet("Claims")
    cell = ws.find(str(user_id), in_column=1)
    if cell is None:
        return None
    return ws.cell(cell.row, 4).value  # col D = promo_code


def save_claim(user_id: int, username: str, promo_name: str, promo_code: str):
    ws = get_worksheet("Claims")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([str(user_id), username, promo_name, promo_code, now])
