import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def add_movie(msg_id, title, full_title, link):
    """Saves both a clean searchable title and a detailed display title."""
    try:
        supabase.table("movies").upsert(
            {
                "message_id": msg_id,
                "title": title,         # For A-Z and Search Logic
                "full_title": full_title, # For User Display (S01, 1080p, etc.)
                "link": link
            },
            on_conflict="message_id" 
        ).execute()
    except Exception as e:
        print(f"Error upserting {title}: {e}")

def search_movies(query):
    """Prioritized search: Phrase match first, then keyword split."""
    exact = supabase.table("movies").select("*").ilike("title", f"%{query}%").execute()
    if exact.data:
        return exact.data

    words = query.split()
    if len(words) > 1:
        search_filter = " or ".join([f"title.ilike.%{word}%" for word in words])
        related = supabase.table("movies").select("*").or_(search_filter).execute()
        return related.data
    return []

def get_movies_by_letter(letter):
    """Fetches movies for the A-Z Index."""
    response = supabase.table("movies").select("*").ilike("title", f"{letter}%").order("title").execute()
    return response.data