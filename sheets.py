# ============================================================
#  sheets.py — Complete Google Sheets backend (fixed for your bot)
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
    "https://www.googleapis.com/auth/drive"
]

_spreadsheet = None


def get_spreadsheet():
    """Get (and cache) the spreadsheet object"""
    global _spreadsheet
    if _spreadsheet is None:
        try:
            creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if not creds_json:
                raise ValueError("Missing GOOGLE_CREDENTIALS_JSON env var")

            creds_dict = json.loads(creds_json)
            sheet_id = os.getenv("GOOGLE_SHEET_ID")

            logger.info(f"🔑 Using service account: {creds_dict.get('client_email')}")
            logger.info(f"📊 Opening spreadsheet ID: {sheet_id}")

            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            client = gspread.authorize(creds)
            _spreadsheet = client.open_by_key(sheet_id)
            logger.info("✅ Successfully connected to Google Spreadsheet!")

        except Exception as e:
            logger.error(f"❌ Sheets init failed: {e}")
            raise
    return _spreadsheet


def get_worksheet(name: str):
    """Get a worksheet by name"""
    ss = get_spreadsheet()
    return ss.worksheet(name)


def setup_sheets():
    """Called from main.py — initializes everything"""
    logger.info("Setting up Google Sheets...")
    try:
        get_worksheet("Members")
        get_worksheet("Claims")
        logger.info("✅ All worksheets loaded successfully")
    except Exception as e:
        logger.error(f"Failed to setup sheets: {e}")
        raise


# ====================== USER LANGUAGE ======================
def set_user_language(user_id: int, lang: str):
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    if cell:
        ws.update_cell(cell.row, 4, lang)          # Column D = Language
    else:
        ws.append_row([str(user_id), "", "", lang, "", 0, datetime.now().isoformat()])


def get_user_language(user_id: int) -> str | None:
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    if cell:
        return ws.cell(cell.row, 4).value
    return None


# ====================== INVITE LINK & COUNT ======================
def save_member(user_id: int, username: str, full_name: str, lang: str, invite_link: str):
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    now = datetime.now().isoformat()
    if cell:
        row = cell.row
        ws.update(f"D{row}:F{row}", [[lang, invite_link, 0]])
    else:
        ws.append_row([str(user_id), username, full_name, lang, invite_link, 0, now])


def get_user_invite_link(user_id: int) -> str | None:
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    if cell:
        return ws.cell(cell.row, 5).value   # Column E = InviteLink
    return None


def remove_invite_link(user_id: int):
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    if cell:
        ws.update_cell(cell.row, 5, "")     # Clear link
        ws.update_cell(cell.row, 6, 0)      # Reset count


def get_invite_count(user_id: int) -> int:
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    if cell:
        count = ws.cell(cell.row, 6).value
        return int(count) if count else 0
    return 0


def increment_invite_count(user_id: int) -> int:
    ws = get_worksheet("Members")
    cell = ws.find(str(user_id), in_column=1)
    if cell:
        current = int(ws.cell(cell.row, 6).value or 0)
        new_count = current + 1
        ws.update_cell(cell.row, 6, new_count)
        return new_count
    return 0


def get_link_owner(invite_link: str) -> int | None:
    ws = get_worksheet("Members")
    cell = ws.find(invite_link, in_column=5)
    if cell:
        user_id = ws.cell(cell.row, 1).value
        return int(user_id) if user_id else None
    return None


# ====================== CLAIMS ======================
def get_claimed_promo(user_id: int) -> str | None:
    ws = get_worksheet("Claims")
    cell = ws.find(str(user_id), in_column=1)
    if cell:
        return ws.cell(cell.row, 3).value   # PromoName
    return None


def save_claim(user_id: int, username: str, promo_name: str, promo_code: str):
    ws = get_worksheet("Claims")
    now = datetime.now().isoformat()
    ws.append_row([str(user_id), username, promo_name, promo_code, now])
