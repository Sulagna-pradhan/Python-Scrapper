import yt_dlp
import json
import datetime

def get_playlist_info(url):
    # Configure yt-dlp options
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # Ensures we get metadata without downloading videos
        'force_generic_extractor': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Fetch playlist metadata
            result = ydl.extract_info(url, download=False)
            
            if 'entries' not in result:
                return "Not a valid playlist URL"

            video_list = []
            total_seconds = 0

            # Process individual videos
            for index, entry in enumerate(result['entries'], start=1):
                duration_sec = entry.get('duration') or 0
                total_seconds += duration_sec
                
                # Format individual duration (MM:SS or HH:MM:SS)
                duration_str = str(datetime.timedelta(seconds=duration_sec)).lstrip('0:')
                if not duration_str: duration_str = "0:00"

                video_data = {
                    "id": f"v{index}",
                    "title": entry.get('title'),
                    "youtubeId": entry.get('id'),
                    "duration": duration_str,
                    "description": entry.get('description') or "No description available."
                }
                video_list.append(video_data)

            # Calculate total duration string (e.g., 2h 45m)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            total_duration_formatted = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            # Construct final JSON structure
            playlist_data = {
                "playlists": [
                    {
                        "id": result.get('id'),
                        "title": result.get('title'),
                        "description": result.get('description') or "No description available.",
                        "category": "Law Entrance", # Static as per your requirement
                        "totalDuration": total_duration_formatted,
                        "videos": video_list
                    }
                ]
            }

            return json.dumps(playlist_data, indent=2)

        except Exception as e:
            return f"Error: {str(e)}"

# Usage
playlist_url = "https://youtube.com/playlist?list=PL3eZ_BXuxJh6ZY6uuJwI-c-0jRjub4n9o&si=RF0O2T7x3Xgii1Gi"
json_output = get_playlist_info(playlist_url)

print(json_output)