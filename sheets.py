import os
import json
import logging
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

# Scopes needed for Google Sheets + Drive (Drive scope sometimes helps with permissions)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Global cache for the spreadsheet object
_spreadsheet: gspread.Spreadsheet | None = None


def get_spreadsheet() -> gspread.Spreadsheet:
    """Get (and cache) the spreadsheet object with full debug logging"""
    global _spreadsheet

    if _spreadsheet is None:
        try:
            # Load credentials from Railway environment variable
            creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if not creds_json:
                logger.error("❌ GOOGLE_CREDENTIALS_JSON environment variable is missing!")
                raise ValueError("Missing GOOGLE_CREDENTIALS_JSON")

            creds_dict = json.loads(creds_json)

            # ==================== DEBUG LOGS (VERY IMPORTANT) ====================
            client_email = creds_dict.get("client_email")
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            logger.info(f"🔑 Using service account: {client_email}")
            logger.info(f"📊 Opening spreadsheet ID: {sheet_id}")
            # =====================================================================

            if not sheet_id:
                logger.error("❌ GOOGLE_SHEET_ID environment variable is missing!")
                raise ValueError("Missing GOOGLE_SHEET_ID")

            # Authorize and open
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            client = gspread.authorize(creds)

            _spreadsheet = client.open_by_key(sheet_id)
            logger.info("✅ Successfully connected to Google Spreadsheet!")

        except json.JSONDecodeError:
            logger.error("❌ GOOGLE_CREDENTIALS_JSON is not valid JSON")
            raise
        except Exception as e:
            logger.error(f"❌ Sheets init failed: {e}")
            raise

    return _spreadsheet


def get_worksheet(name: str) -> gspread.Worksheet:
    """Get a worksheet by its exact name"""
    ss = get_spreadsheet()
    return ss.worksheet(name)


def setup_sheets():
    """Called from main.py - initializes all worksheets"""
    logger.info("Setting up Google Sheets...")
    try:
        members_ws = get_worksheet("Members")
        # Add more worksheets here if you use them later:
        # logs_ws = get_worksheet("Logs")
        # settings_ws = get_worksheet("Settings")

        logger.info("✅ All worksheets loaded successfully")
        
        # Return them so main.py can use them if needed
        return {
            "members": members_ws,
            # "logs": logs_ws,      # uncomment when you add more sheets
        }

    except Exception as e:
        logger.error(f"Failed to setup sheets: {e}")
        raise
