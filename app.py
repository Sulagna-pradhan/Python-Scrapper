from __future__ import annotations

import os
from typing import Callable
from pathlib import Path


ROOT = Path(__file__).resolve().parent

def run_movie_indexer() -> int:
    from src.integrations.telegram.movie_indexer import client, main

    client.loop.run_until_complete(main())
    return 0


def run_movie_search_bot() -> int:
    from dotenv import load_dotenv
    from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters
    from src.integrations.telegram.movie_search_bot import cb_handler, handle_search, start

    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN must be set in environment")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search))
    app.add_handler(CallbackQueryHandler(cb_handler))
    app.run_polling()
    return 0


def run_channel_forwarder() -> int:
    from src.integrations.telegram.channel_forwarder import client, main

    client.loop.run_until_complete(main())
    return 0


def run_channel_downloader() -> int:
    from src.integrations.telegram.channel_downloader import main

    main()
    return 0


def run_telegram_uploader() -> int:
    from src.services.telegram_uploader import app

    app.run(debug=True, port=5000)
    return 0


def run_imgbb_uploader() -> int:
    from src.integrations.imgbb_upload import client, process_channel

    target = input("Enter Telegram Channel Username or Link: ").strip()
    local_enabled = input("Enable local download? (yes/no): ").strip().lower() == "yes"
    with client:
        client.loop.run_until_complete(process_channel(target, local_enabled))
    return 0


def run_cu_notice_scraper() -> int:
    from src.scrapers.university.cu_notices import scrape_notices

    scrape_notices()
    return 0


def run_gfg_article_exporter() -> int:
    from src.scrapers.content.geeksforgeeks_article import main

    main()
    return 0


def run_youtube_audio_downloader() -> int:
    from src.scrapers.youtube.audio_downloader import download_youtube_audio

    video_url = input("Enter the YouTube URL: ").strip()
    download_youtube_audio(video_url)
    return 0


def run_playlist_extractor() -> int:
    import os
    from src.scrapers.youtube.playlist_extractor import OUTPUT_DIR, get_playlist_info

    playlist_url = input("Enter YouTube playlist URL: ").strip()
    json_output = get_playlist_info(playlist_url)
    if json_output.startswith("Error:") or json_output == "Not a valid playlist URL":
        print(json_output)
        return 1

    output_path = os.path.join(OUTPUT_DIR, "playlist_info.json")
    with open(output_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(json_output)
    print(f"Saved: {output_path}")
    return 0


WORKFLOWS: list[tuple[str, str, Callable[[], int]]] = [
    ("Telegram", "Movie indexer", run_movie_indexer),
    ("Telegram", "Movie search bot", run_movie_search_bot),
    ("Telegram", "Channel forwarder", run_channel_forwarder),
    ("Telegram", "Channel downloader", run_channel_downloader),
    ("Telegram", "Telegram uploader", run_telegram_uploader),
    ("Telegram", "ImgBB uploader", run_imgbb_uploader),
    ("University", "CU notice scraper", run_cu_notice_scraper),
    ("GeeksforGeeks", "Article exporter", run_gfg_article_exporter),
    ("YouTube", "Audio downloader", run_youtube_audio_downloader),
    ("YouTube", "Playlist extractor", run_playlist_extractor),
]


def show_menu() -> None:
    print("\nPython Scraper Launcher\n")
    current_group = None
    for index, (group, title, _) in enumerate(WORKFLOWS, start=1):
        if group != current_group:
            current_group = group
            print(f"[{group}]")
        print(f"  {index}. {title}")
    print("  0. Exit\n")


def run_choice(choice: int) -> int:
    if choice < 1 or choice > len(WORKFLOWS):
        return 0

    _, title, action = WORKFLOWS[choice - 1]

    print(f"\nRunning {title}\n")
    exit_code = action()
    print(f"\nFinished {title} with exit code {exit_code}\n")
    return exit_code


def main() -> int:
    while True:
        show_menu()
        raw_choice = input("Choose a script to run: ").strip()

        if raw_choice == "0":
            print("Exiting.")
            return 0

        if not raw_choice.isdigit():
            print("Enter a valid number.")
            continue

        exit_code = run_choice(int(raw_choice))
        if exit_code != 0:
            print(f"Script finished with exit code {exit_code}")


if __name__ == "__main__":
    raise SystemExit(main())