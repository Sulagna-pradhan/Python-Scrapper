import asyncio
import os
import re
from telethon import TelegramClient
from database import add_movie
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel_id = -1002478481734 

def clean_movie_title(raw_text):
    if not raw_text: return "Unknown Title"
    text = raw_text.replace("**", "").replace("__", "")
    patterns = [r'\(\d{4}\)', r'S\d{2}', r'\d{3,4}p', r'WEBRip', r'HDRip', r'\[.*\]', r'~.*', r'\.mkv$', r'\.mp4$']
    first_index = len(text)
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: first_index = min(first_index, match.start())
    clean_name = text[:first_index].replace(".", " ").replace("-", " ").strip()
    return clean_name.upper()

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()
    print("🚀 Syncing and Cleaning Titles...")
    count = 0
    async for message in client.iter_messages(channel_id):
        if message.text and (message.video or message.document):
            raw_title = message.text.split('\n')[0].strip()
            clean_title = clean_movie_title(raw_title)
            msg_id = message.id
            clean_cid = str(channel_id).replace("-100", "")
            link = f"https://t.me/c/{clean_cid}/{msg_id}"
            add_movie(msg_id, clean_title, link)
            count += 1
            print(f"✅ Indexed: {clean_title}")
    print(f"🏁 Done! Total: {count}")

if __name__ == '__main__':
    with client: client.loop.run_until_complete(main())