import os
import time
import zipfile
import threading
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================

BOT_TOKEN = "8111668670:AAHYbYB3-sUb_Cok9YNVoKYensT4eobNIwI"  # <-- paste locally
IDLE_TIMEOUT = 10  # seconds

# ================== USER INPUT ==================

folder_name = input("Enter download folder name: ").strip()
if not folder_name:
    folder_name = "downloads"

DOWNLOAD_DIR = os.path.join("downloads", folder_name)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

last_message_time = time.time()
stop_event = threading.Event()

# ================== HANDLER ==================

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_message_time

    post = update.channel_post
    if not post or not post.photo:
        return

    photo = post.photo[-1]
    file = await photo.get_file()

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{post.chat.username}_{post.message_id}.jpg"
    )

    await file.download_to_drive(file_path)

    last_message_time = time.time()
    print(f"✅ Image downloaded: {file_path}")

# ================== ZIP FUNCTION ==================

def zip_downloads():
    zip_path = f"{DOWNLOAD_DIR}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(DOWNLOAD_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, arcname=file)
    print(f"\n📦 ZIP created: {zip_path}")

# ================== IDLE WATCHER ==================

def idle_watcher(app: Application):
    global last_message_time

    while not stop_event.is_set():
        time.sleep(2)
        idle_time = time.time() - last_message_time

        if idle_time >= IDLE_TIMEOUT:
            answer = input("\n⏸ No new messages.\nAre you done? (y/N): ").strip().lower()
            if answer == "y":
                print("🛑 Stopping bot...")
                stop_event.set()
                app.stop()
                zip_downloads()
                break
            else:
                print("▶ Continuing...")
                last_message_time = time.time()

# ================== MAIN ==================

def main():
    if not BOT_TOKEN or "PASTE_YOUR_BOT_TOKEN_HERE" in BOT_TOKEN:
        raise RuntimeError("❌ Bot token not set")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.PHOTO & filters.ChatType.CHANNEL, handle_channel_post)
    )

    print("🤖 Bot is running...")

    watcher_thread = threading.Thread(
        target=idle_watcher, args=(app,), daemon=True
    )
    watcher_thread.start()

    app.run_polling()

if __name__ == "__main__":
    main()
