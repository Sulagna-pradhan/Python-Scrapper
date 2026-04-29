import os
import re
from telethon import TelegramClient
from src.services.movie_database import add_movie
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

api_id = int(os.getenv("API_ID", "0"))
api_hash = os.getenv("API_HASH")
channel_id = int(os.getenv("MOVIE_CHANNEL_ID", "-1002478481734"))

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SESSION_DIR = PROJECT_ROOT / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)
SESSION_PATH = str(SESSION_DIR / "movie_indexer")

def clean_movie_title(raw_text):
    """Creates a very clean version for grouping and A-Z sorting."""
    if not raw_text: return "UNKNOWN"
    text = raw_text.replace("**", "").replace("__", "")
    patterns = [r'\(\d{4}\)', r'S\d{2}', r'\d{3,4}p', r'WEBRip', r'HDRip', r'\[.*\]', r'~.*', r'\.mkv$', r'\.mp4$']
    first_index = len(text)
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: first_index = min(first_index, match.start())
    return text[:first_index].replace(".", " ").replace("-", " ").strip().upper()

if not api_id or not api_hash:
    raise RuntimeError("API_ID and API_HASH must be set in environment")

client = TelegramClient(SESSION_PATH, api_id, api_hash)

async def main():
    await client.start()
    print("🚀 Syncing Channel with Dual-Title System...")
    count = 0
    async for message in client.iter_messages(channel_id):
        if message.text and (message.video or message.document):
            raw_line = message.text.split('\n')[0].strip()
            
            clean_t = clean_movie_title(raw_line)
            full_t = raw_line.replace("**", "").strip() # Keeps quality/episode info
            
            link = f"https://t.me/c/{str(channel_id).replace('-100', '')}/{message.id}"
            add_movie(message.id, clean_t, full_t, link)
            count += 1
            print(f"✅ Indexed: {clean_t}")
            
    print(f"🏁 Sync Complete. Total: {count}")

if __name__ == '__main__':
    with client: client.loop.run_until_complete(main())