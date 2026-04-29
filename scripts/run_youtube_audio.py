from src.scrapers.youtube.audio_downloader import download_youtube_audio


if __name__ == "__main__":
    video_url = input("Enter the YouTube URL: ").strip()
    download_youtube_audio(video_url)
