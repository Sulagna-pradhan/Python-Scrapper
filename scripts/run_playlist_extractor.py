from src.scrapers.youtube.playlist_extractor import get_playlist_info, OUTPUT_DIR
import os


if __name__ == "__main__":
    playlist_url = input("Enter YouTube playlist URL: ").strip()
    json_output = get_playlist_info(playlist_url)
    if json_output.startswith("Error:") or json_output == "Not a valid playlist URL":
        print(json_output)
    else:
        output_path = os.path.join(OUTPUT_DIR, "playlist_info.json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"Saved: {output_path}")
