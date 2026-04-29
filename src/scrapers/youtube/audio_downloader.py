import yt_dlp
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "downloads", "youtube")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_youtube_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(OUTPUT_DIR, '%(title)s.%(ext)s'),
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {link}")
            ydl.download([link])
        print("\nDownload complete!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    video_url = input("Enter the YouTube URL: ")
    download_youtube_audio(video_url)