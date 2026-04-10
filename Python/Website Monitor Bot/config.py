import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN        = os.getenv("BOT_TOKEN")
CHAT_ID          = os.getenv("CHAT_ID")
CHECK_INTERVAL   = int(os.getenv("CHECK_INTERVAL", 60))  # seconds
STORAGE_FILE     = "sites.json"
REQUEST_TIMEOUT  = 10   # seconds per HTTP check
MAX_SITES        = 50   # max sites per instance