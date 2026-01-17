# 🚀 Telegram to ImgBB Scraper & Metadata Logger

A robust, asynchronous Python tool built with **Telethon** and **Requests** to archive public Telegram channel images. This script fetches media from Telegram, uploads it to **ImgBB** via API, and maintains a detailed JSON database of all successful transfers.

---

## 🛠 Features

* **Hybrid Storage Logic:** * **Memory Path:** Streams images directly to ImgBB using `io.BytesIO` to save disk space.
* **Local Path (Optional):** Toggle-able local downloads to keep a physical backup.


* **Automatic Metadata Export:** Generates a structured `image_metadata.json` containing direct links, delete URLs, and Telegram message references.
* **Anti-Flood Protection:** Handles Telegram's `FloodWaitError` automatically to prevent account bans.
* **Smart Link Parsing:** Automatically extracts usernames from full Telegram URLs (e.g., `https://t.me/channel_name`).

---

## 🏗 System Architecture

The script operates as an intermediary bridge between Telegram's servers and ImgBB's cloud storage.

1. **Authentication:** Establishes a secure session using Telegram API credentials.
2. **Streaming:** Downloads media into RAM as a byte-stream.
3. **Uploading:** Dispatches a `POST` request to ImgBB with the binary data.
4. **Logging:** Merges responses from both APIs into a single JSON entry for easy tracking.

---

## 🚀 Installation & Setup

### 1. Requirements

Install the necessary Python dependencies:

```bash
pip install telethon requests

```

### 2. Configuration

Edit the configuration variables in `app.py`:

* **API_ID / API_HASH:** Obtain these from [my.telegram.org](https://my.telegram.org).
* **IMGBB_API_KEY:** Obtain this from [api.imgbb.com](https://api.imgbb.com/).

### 3. Execution

Run the script:

```bash
python3 app.py

```

---

## 📋 Usage Guide

1. **Input:** When prompted, enter the Telegram channel username or the full URL.
2. **Local Mode:** * Type `yes` to save a copy in the `/downloads` folder.
* Type `no` to keep your environment clean and only upload to the cloud.


3. **Telegram Login:** On your first run, you will need to enter your phone number and the verification code received on your Telegram app.

---

## 📊 JSON Data Format

Each entry in `image_metadata.json` follows this schema:

```json
{
    "telegram": {
        "channel": "",
        "msg_id": 163,
        "date": "2026-01-17 13:45:00",
        "local_path": "downloads/"
    },
    "imgbb": {
        "id": "abc123XYZ",
        "url": "https://i.ibb.co/direct-link.jpg",
        "display_url": "https://ibb.co/preview-link",
        "size": 102400,
        "delete_url": "https://ibb.co/delete/secret-key",
        "mime": "image/jpeg"
    }
}

```

---

## ⚠️ Safety & Limitations

* **Rate Limiting:** A default delay of **3 seconds** is added between uploads. Reducing this significantly may result in a temporary ban on your Telegram account.
* **Private Channels:** This script is designed for **public** channels. Scraping private channels requires the account to be a member of that channel.
* **Storage:** If "Local Download" is enabled, ensure your environment (like GitHub Codespaces) has sufficient disk space for the volume of images expected.

---