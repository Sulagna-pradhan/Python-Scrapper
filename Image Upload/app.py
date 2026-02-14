import os
import asyncio
import io
import json
import requests
from telethon import TelegramClient, errors

# --- CONFIGURATION ---
API_ID = ''
API_HASH = ''
IMGBB_API_KEY = '' 
METADATA_FILE = 'image_metadata.json'
BASE_SAVE_FOLDER = 'downloads'

client = TelegramClient('session_name', API_ID, API_HASH)

def save_metadata(new_entry):
    """Appends metadata to a JSON file."""
    data = []
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    
    data.append(new_entry)
    with open(METADATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

async def upload_to_imgbb(image_bytes, filename):
    """Uploads binary data and returns the full API response metadata."""
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "name": filename,
    }
    files = {"image": image_bytes}
    
    try:
        response = requests.post(url, payload, files=files)
        response_data = response.json()
        
        if response_data.get('status') == 200:
            return response_data['data']
        else:
            print(f"ImgBB Error: {response_data.get('error', {}).get('message', 'Unknown Error')}")
            return None
    except Exception as e:
        print(f"Failed to upload to ImgBB: {e}")
        return None

async def process_channel(target_input, enable_local):
    # Clean the input: Remove 'https://t.me/' or '@'
    channel_username = target_input.split('/')[-1].replace('@', '')
    
    await client.start()
    print(f"Connected. Processing @{channel_username}...")

    # Create local directory if enabled
    local_path = ""
    if enable_local:
        local_path = os.path.join(BASE_SAVE_FOLDER, channel_username)
        if not os.path.exists(local_path):
            os.makedirs(local_path)
            print(f"Local storage enabled. Images will be saved to: {local_path}")

    count = 0
    async for message in client.iter_messages(channel_username, limit=None):
        if message.photo:
            filename = f"{channel_username}_{message.id}.jpg"
            
            try:
                print(f"Fetching {filename} from Telegram...")
                
                # Download to memory first for ImgBB
                buffer = io.BytesIO()
                await message.download_media(file=buffer)
                image_bytes = buffer.getvalue()
                
                # --- LOCAL DOWNLOAD LOGIC ---
                if enable_local:
                    full_local_file = os.path.join(local_path, filename)
                    with open(full_local_file, 'wb') as f:
                        f.write(image_bytes)
                
                # --- IMGBB UPLOAD LOGIC ---
                metadata = await upload_to_imgbb(image_bytes, filename)
                
                if metadata:
                    # Enrich metadata
                    full_entry = {
                        "telegram": {
                            "channel": channel_username,
                            "msg_id": message.id,
                            "date": str(message.date),
                            "local_path": os.path.join(local_path, filename) if enable_local else "None"
                        },
                        "imgbb": metadata
                    }
                    save_metadata(full_entry)
                    count += 1
                    print(f"[{count}] Uploaded! URL: {metadata['url']}")
                
                # Flood protection delay
                await asyncio.sleep(3)

            except errors.FloodWaitError as e:
                print(f"Telegram Limit! Waiting {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"\n--- Task Finished ---")
    print(f"Total entries saved to {METADATA_FILE}")

if __name__ == '__main__':
    target = input("Enter Telegram Channel Username or Link: ")
    
    # Prompt for local download
    choice = input("Enable local download? (yes/no): ").strip().lower()
    local_enabled = choice == 'yes'
    
    with client:
        client.loop.run_until_complete(process_channel(target, local_enabled))