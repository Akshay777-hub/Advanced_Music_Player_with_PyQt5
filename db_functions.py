import os
import json
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

url: str = "https://mrxbxtuptrdmfgvdbofk.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yeGJ4dHVwdHJkbWZndmRib2ZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyODkzNzU5NCwiZXhwIjoyMDQ0NTEzNTk0fQ.NBHq2-TKoKCFHCLUXX9knYVexbN6urrL0EdKJxPrzZE"

options: ClientOptions = ClientOptions(headers={'Authorization': f'Bearer {key}'})
supabase: Client = create_client(url, key)

def delete_playlist(playlist_name):
    try:
        supabase.table('playlists').delete().eq('playlist_name', playlist_name).execute()
        supabase.table('playlist_songs').delete().eq('playlist_name', playlist_name).execute() # Delete associated songs
        print(f"Deleted playlist: {playlist_name}")
    except Exception as e:
        print(f"Error deleting playlist: {e}")

def get_all_playlists():
    try:
        data = supabase.table('playlists').select('playlist_name').execute()
        playlists = [item['playlist_name'] for item in data.data] if data.data else []
        return playlists
    except Exception as e:
        print(f"Error getting playlists: {e}")
        return []
    

# Add a song to a database table
def add_song_to_database_table(song: str, table: str, uuid: str):
    try:
        data = {"song": song, "user_uuid": uuid}
        supabase.table(table).insert(data).execute()
        print(f"Inserted song: {song} into table: {table}")
    except Exception as e:
        print(f"Error inserting song: {e}")

def add_song_to_playlist(playlist_name, song_path):
    try:
        data = {'playlist_name': playlist_name, 'song_path': song_path}
        supabase.table('playlist_songs').insert(data).execute()
        print(f"Added song {song_path} to playlist {playlist_name}")
    except Exception as e:
        print(f"Error adding song to playlist: {e}")


# Delete a song from a database table
def delete_song_from_database_table(song: str, table: str):
    try:
        data = (
            supabase.table(table)
            .delete()
            .eq("song", song)
            .execute()
        )
        print(f"Deleted song: {song} from table: {table}")
    except Exception as e:
        print(f"Error deleting song: {e}")



# Delete all songs from a database table
def delete_all_songs_from_database_table(table: str):
    try:
        data = supabase.table(table).delete().execute()
        print(f"Deleted all songs from table: {table}")

    except Exception as e:
        print(f"Error deleting all song: {e}")


# Fetch all songs from a database table
def fetch_all_songs_from_database_table(table: str):
    try:
        data = supabase.table(table).select("song").execute()
        songs = [item["song"] for item in data.data]
        return songs

    except Exception as e:
        print(f"Error fetching songs: {e}")

def delete_playlist(playlist_name):
    try:
        supabase.table('playlists').delete().eq('playlist_name', playlist_name).execute()
        supabase.table('playlist_songs').delete().eq('playlist_name', playlist_name).execute() # Delete associated songs
        print(f"Deleted playlist: {playlist_name}")
    except Exception as e:
        print(f"Error deleting playlist: {e}")


# Get all tables in the database
def get_all_playlists():
    try:
        data = supabase.table('playlists').select('playlist_name').execute()
        playlists = [item['playlist_name'] for item in data.data] if data.data else []
        return playlists
    except Exception as e:
        print(f"Error getting playlists: {e}")
        return []
    
def get_playlist_songs(playlist_name):
    try:
        # Get playlist id
        playlist_data = supabase.table('playlists').select('id').eq('playlist_name', playlist_name).execute()
        playlist_id = playlist_data.data[0]['id'] if playlist_data.data else None

        if playlist_id: # Check if playlist_id exists
            # Get songs using playlist_id
            data = supabase.table('playlist_songs').select('song_path').eq('playlist_id', playlist_id).execute()
            songs = [item['song_path'] for item in data.data] if data.data else []
            return songs
        else:
            print(f"Playlist '{playlist_name}' not found.") # Handle the case where the playlist is not found
            return []

    except Exception as e:
        print(f"Error getting playlist songs: {e}")
        return []

    
def get_all_schemas():
    try:
        response = supabase.postgrest.client().from_("information_schema.schemata").select("schema_name").execute()
        schemas = [item["schema_name"] for item in response.data] if response.data else []
        return schemas
    except Exception as e:
        print(f"Error getting schemas: {e}")
        return []


# Delete a database table
def delete_database_table(table: str):
    try:
        supabase.table(table).delete().execute()
    except Exception as e:
        print(f"Error deleting table: {e}")

def create_playlist(playlist_name, user_uuid):  # Add user_id if needed
    try:
        data = {'playlist_name': playlist_name, 'user_uuid':user_uuid}
        supabase.table('playlists').insert(data).execute()
        print(f"Created playlist: {playlist_name}")
    except Exception as e:
        print(f"Error creating playlist: {e}")
