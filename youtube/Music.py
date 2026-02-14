import yt_dlp

def download_youtube_mp3(url):
    # Configuration options for yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',  # Get the best quality audio
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',   # Convert to MP3
            'preferredquality': '192', # Bitrate
        }],
        'outtmpl': '%(title)s.%(ext)s', # Save file as the video title
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Starting download: {url}")
            ydl.download([url])
            print("\nDownload and conversion complete!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    video_url = input("Enter the YouTube URL: ")
    download_youtube_mp3(video_url)