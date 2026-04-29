# Python-Scraper

Production-oriented Python scraper and Telegram automation toolkit.

## Project Layout

```
.
├── src/
│   ├── scrapers/
│   │   ├── university/cu_notices.py
│   │   ├── content/geeksforgeeks_article.py
│   │   └── youtube/
│   │       ├── audio_downloader.py
│   │       └── playlist_extractor.py
│   ├── integrations/
│   │   ├── imgbb_upload.py
│   │   └── telegram/
│   │       ├── movie_indexer.py
│   │       ├── movie_search_bot.py
│   │       ├── channel_downloader.py
│   │       ├── post_downloader.py
│   │       └── channel_forwarder.py
│   └── services/
│       ├── movie_database.py
│       └── telegram_uploader.py
├── scripts/
├── data/
├── sessions/
├── docs/
├── .env.example
└── requirements.txt
```

## Quick Start

1. Create virtual environment and install dependencies.
2. Copy .env.example to .env and set required values.
3. Use runner scripts from scripts/.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Runner Commands

```bash
python scripts/run_movie_indexer.py
python scripts/run_movie_search_bot.py
python scripts/run_channel_forwarder.py
python scripts/run_channel_downloader.py
python scripts/run_telegram_uploader.py
python scripts/run_imgbb_upload.py
python scripts/run_cu_notices.py
python scripts/run_gfg_article_export.py
python scripts/run_youtube_audio.py
python scripts/run_playlist_extractor.py
```

## Runtime Conventions

- Generated files are written under data/.
- Telethon session artifacts are stored under sessions/.
- Secrets are loaded from environment variables (.env).

## Disclaimer

This repository is for educational and automation use. Ensure your usage complies with platform policies and applicable laws.
