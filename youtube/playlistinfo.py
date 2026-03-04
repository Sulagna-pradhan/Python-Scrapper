import yt_dlp
import json
import datetime

def get_playlist_info(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(url, download=False)
            
            if 'entries' not in result:
                return "Not a valid playlist URL"

            video_list = []
            total_seconds = 0

            for index, entry in enumerate(result['entries'], start=1):
                duration_sec = entry.get('duration') or 0
                total_seconds += duration_sec
                
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

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            total_duration_formatted = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            playlist_data = {
                "playlists": [
                    {
                        "id": result.get('id'),
                        "title": result.get('title'),
                        "description": result.get('description') or "No description available.",
                        "category": "Law Entrance",
                        "totalDuration": total_duration_formatted,
                        "videos": video_list
                    }
                ]
            }

            return json.dumps(playlist_data, indent=2)

        except Exception as e:
            return f"Error: {str(e)}"

playlist_url = "https://youtube.com/playlist?list=PL3eZ_BXuxJh6ZY6uuJwI-c-0jRjub4n9o&si=RF0O2T7x3Xgii1Gi"
json_output = get_playlist_info(playlist_url)

print(json_output)