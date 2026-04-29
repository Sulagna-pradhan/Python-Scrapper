# Python-Scraper

Launcher-driven Python scraper and Telegram automation toolkit.

The main entry point is [app.py](app.py). It shows a numbered menu of all available workflows and runs the one you choose.

## How To Run

1. Create a virtual environment and install dependencies.
2. Copy [.env.example](.env.example) to `.env` and fill in the required values.
3. Start the launcher with `python app.py`.
4. Pick a number from the menu.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Project Organization

The codebase is organized by responsibility, not by one-off scripts.

### Root files

- [app.py](app.py): interactive launcher for the full repo
- [requirements.txt](requirements.txt): single dependency file for the whole project
- [.env.example](.env.example): environment variable template

### `src/`

Core application code lives here.

- [src/scrapers/university/cu_notices.py](src/scrapers/university/cu_notices.py): Calcutta University notice scraper
- [src/scrapers/content/geeksforgeeks_article.py](src/scrapers/content/geeksforgeeks_article.py): GeeksforGeeks article exporter
- [src/scrapers/youtube/audio_downloader.py](src/scrapers/youtube/audio_downloader.py): YouTube audio downloader
- [src/scrapers/youtube/playlist_extractor.py](src/scrapers/youtube/playlist_extractor.py): YouTube playlist metadata extractor
- [src/integrations/imgbb_upload.py](src/integrations/imgbb_upload.py): ImgBB and Telegram image workflow
- [src/integrations/telegram/movie_indexer.py](src/integrations/telegram/movie_indexer.py): movie indexing sync
- [src/integrations/telegram/movie_search_bot.py](src/integrations/telegram/movie_search_bot.py): movie search bot
- [src/integrations/telegram/channel_forwarder.py](src/integrations/telegram/channel_forwarder.py): Telegram forwarder
- [src/integrations/telegram/channel_downloader.py](src/integrations/telegram/channel_downloader.py): channel image downloader
- [src/integrations/telegram/post_downloader.py](src/integrations/telegram/post_downloader.py): post image downloader
- [src/services/movie_database.py](src/services/movie_database.py): Supabase data layer for movie search/indexing
- [src/services/telegram_uploader.py](src/services/telegram_uploader.py): Flask-based Telegram uploader

### `scripts/`

This folder contains thin runner scripts used by the launcher. They make each workflow executable as a dedicated entrypoint while keeping the implementation inside `src/`.

### `data/`

Generated files and exports go here, including downloaded media and exported documents.

### `sessions/`

Telethon session files are stored here so they stay out of the source folders.

### `docs/`

Documentation and reference materials live here.

## Menu Workflow

When you run `python app.py`, the launcher shows the available workflows grouped by domain:

- Telegram
- University
- GeeksforGeeks
- YouTube

Select the number for the workflow you want. The launcher will prompt for any additional input that script needs.

## Environment Variables

The repo expects secrets and API values in `.env`. Common values include:

- `API_ID`
- `API_HASH`
- `BOT_TOKEN`
- `MOVIE_CHANNEL_ID`
- `UPLOAD_CHANNEL_ID`
- `AUTH_CHANNEL`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `IMGBB_API_KEY`

## Runtime Conventions

- Generated exports are written under `data/`.
- Telethon sessions are written under `sessions/`.
- Secrets are never committed to the repo.
- `requirements.txt` is the single dependency source for the full codebase.

## Notes

- Some workflows require additional setup in Telegram, Supabase, or ImgBB before they can run successfully.
- If a menu option fails, first check that the corresponding environment variables and dependencies are installed.
