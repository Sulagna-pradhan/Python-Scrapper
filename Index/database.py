import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Initialize Supabase Client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def add_movie(msg_id, title, link):
    """
    Inserts a new movie or updates an existing one if message_id exists.
    This prevents 'Duplicate Key' errors during re-scraping.
    """
    try:
        supabase.table("movies").upsert(
            {
                "message_id": msg_id,
                "title": title,
                "link": link
            },
            on_conflict="message_id" # Magic line that updates existing data
        ).execute()
    except Exception as e:
        print(f"Error upserting {title}: {e}")

def search_movies(query):
    """
    Smarter search: 
    1. Looks for exact phrase match.
    2. If fails, splits the query into words to find related results.
    """
    # 1. Try Exact/Phrase Match first (Highest Priority)
    exact_response = supabase.table("movies").select("*").ilike("title", f"%{query}%").execute()
    
    if exact_response.data:
        return exact_response.data

    # 2. Related Match (Fallback)
    # Splits the search into words to find partial matches
    words = query.split()
    if len(words) > 1:
        # Build a filter that matches ANY of the words provided
        search_filter = " or ".join([f"title.ilike.%{word}%" for word in words])
        related_response = supabase.table("movies").select("*").or_(search_filter).execute()
        return related_response.data
        
    return []

def get_all_movies():
    """
    Retrieves all movies sorted alphabetically for the index.
    """
    response = supabase.table("movies").select("*").order("title").execute()
    return response.data