from supabase import create_client, Client

# Configure Supabase
SUPABASE_URL = "https://mrxbxtuptrdmfgvdbofk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yeGJ4dHVwdHJkbWZndmRib2ZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg5Mzc1OTQsImV4cCI6MjA0NDUxMzU5NH0.3v1kGzwEdV8CBql4kQ5iW4ep2cUDxdfdcKThEkuP3ew"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_playlist_table(table_name: str):
    try:
        response = supabase.rpc("create_playlist_table", {"table_name": table_name}).execute()
        if response.status_code != 200:
            print("Error creating table:", response.json())
            return False
        return True
    except Exception as e:
        print(f"Exception while creating table: {e}")
        return False



def add_song_to_playlist(song: str, playlist: str):
    try:
        response = supabase.table(playlist).insert({"song": song}).execute()
        if response.status_code != 201:
            print("Error adding song:", response.json())
            return False  # Indicate failure
        return True  # Indicate success

    except Exception as e:
        print(f"Exception while adding song: {e}")
        return False  # Indicate failure



def delete_song_from_playlist(song: str, playlist: str):
    try:
        response = supabase.table(playlist).delete().eq("song", song).execute()
        if response.status_code != 200:
            print("Error deleting song:", response.json())
            return False
        return True
    except Exception as e:
        print(f"Exception while deleting song: {e}")
        return False


def delete_all_songs_from_playlist(playlist: str):
    try:
        response = supabase.table(playlist).delete().neq("song", "").execute() # It might make more sense to delete everything, not check against empty song
        if response.status_code != 200:
            print("Error deleting all songs:", response.json())
            return False
        return True
    except Exception as e:
        print(f"Exception while deleting all songs: {e}")
        return False



def fetch_all_songs_from_playlist(playlist: str):
    try:
        response = supabase.table(playlist).select("*").execute()
        if response.status_code == 200:
            return [record["song"] for record in response.data]
        else:
            print("Error fetching songs:", response.json())
            return []
    except Exception as e:
        print(f"Exception while fetching songs: {e}")
        return []



def get_playlist_tables():
    try:
        response = supabase.rpc("get_playlist_tables").execute()
        if response.status_code == 200:
            return response.data
        else:
            print("Error getting playlist tables:", response.json())
            return []
    except Exception as e:
        print(f"Exception while getting playlist tables: {e}")
        return []


def delete_playlist_table(table: str):
    try:
        response = supabase.rpc("drop_table", {"table_name": table}).execute()
        if response.status_code != 200:
            print("Error deleting table:", response.json())
            return False  # Indicate failure
        return True  # Indicate Success

    except Exception as e:
        print(f"Exception while deleting table: {e}")
        return False



def add_song_to_favourites(song: str):
    return add_song_to_playlist(song, "favourites")



def delete_song_from_favourites(song: str):
    return delete_song_from_playlist(song, 'favourites')

def delete_all_songs_from_favourites():
    return delete_all_songs_from_playlist('favourites')

def fetch_all_songs_from_favourites():
    return fetch_all_songs_from_playlist("favourites")



def clear_currently_playing(listWidget): # Helper function - new addition
    listWidget.clear()