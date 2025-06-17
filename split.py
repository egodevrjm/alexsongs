import json
import os
import re

def sanitize_filename(name):
    """
    Removes characters that are invalid for file names from a string.
    This helps prevent errors when creating files from song or album titles.
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores for cleaner filenames
    sanitized = sanitized.replace(" ", "_")
    return sanitized

def create_directories(base_path):
    """
    Creates the necessary output directories for songs, albums, and artists.
    """
    print("Creating output directories...")
    os.makedirs(os.path.join(base_path, 'songs'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'albums'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'artists'), exist_ok=True)
    print("Directories created successfully.")

def create_song_files(songs_data, base_path):
    """
    Creates an individual JSON file for each song.
    """
    print(f"Creating individual files for {len(songs_data)} songs...")
    song_dir = os.path.join(base_path, 'songs')
    for song in songs_data:
        # Ensure the item is actually a song with a title
        if 'title' in song and song['title'] != "Profile":
            try:
                # Sanitize title for use as a filename
                filename = f"{sanitize_filename(song['title'])}.json"
                filepath = os.path.join(song_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(song, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Could not create file for song: {song.get('title', 'NO_TITLE')}. Error: {e}")
    print("Song files created.")

def create_album_files(songs_data, base_path):
    """
    Groups songs by album and creates a JSON file for each album.
    """
    print("Grouping songs by album and creating album files...")
    albums = {}
    for song in songs_data:
        # Check if the song belongs to an album
        if song.get('album'):
            album_title = song['album']
            if album_title not in albums:
                albums[album_title] = []
            albums[album_title].append(song)

    album_dir = os.path.join(base_path, 'albums')
    for album_title, songs_in_album in albums.items():
        try:
            filename = f"{sanitize_filename(album_title)}.json"
            filepath = os.path.join(album_dir, filename)
            # Sort songs within the album by title for consistency
            sorted_songs = sorted(songs_in_album, key=lambda x: x.get('title', ''))
            album_data = {
                "album_title": album_title,
                "artist": songs_in_album[0].get('artist', 'Various Artists'),
                "song_count": len(sorted_songs),
                "songs": sorted_songs
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(album_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Could not create file for album: {album_title}. Error: {e}")
    print("Album files created.")


def create_artist_files(songs_data, base_path):
    """
    Groups songs by artist and creates a JSON file for each artist.
    """
    print("Grouping songs by artist and creating artist files...")
    artists = {}
    for song in songs_data:
        # Check if the song has an artist
        if song.get('artist'):
            artist_name = song['artist']
            if artist_name not in artists:
                artists[artist_name] = []
            artists[artist_name].append(song)

    artist_dir = os.path.join(base_path, 'artists')
    for artist_name, songs_by_artist in artists.items():
        try:
            filename = f"{sanitize_filename(artist_name)}.json"
            filepath = os.path.join(artist_dir, filename)
            # Sort songs by title for consistency
            sorted_songs = sorted(songs_by_artist, key=lambda x: x.get('title', ''))
            artist_data = {
                "artist_name": artist_name,
                "song_count": len(sorted_songs),
                "songs": sorted_songs
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(artist_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Could not create file for artist: {artist_name}. Error: {e}")
    print("Artist files created.")

def create_profile_and_metadata_files(data, base_path):
    """
    Extracts profile information and metadata into their own files.
    """
    print("Extracting profile and metadata...")
    # Extract metadata if it exists
    if 'metadata' in data:
        filepath = os.path.join(base_path, 'metadata.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data['metadata'], f, indent=4, ensure_ascii=False)
        print("metadata.json created.")

    # Find and extract the artist profile
    profile_data = next((item for item in data.get('songs', []) if item.get('title') == "Profile"), None)
    if profile_data:
        filepath = os.path.join(base_path, 'artist_profile.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=4, ensure_ascii=False)
        print("artist_profile.json created.")


def create_catalog_file(songs_data, base_path):
    """
    Creates a master catalog file listing all songs, albums, and artists.
    """
    print("Creating master catalog file...")
    catalog = {
        "artists": {},
        "albums": {},
        "songs": []
    }

    # Populate songs list
    catalog['songs'] = sorted([song['title'] for song in songs_data if 'title' in song and song['title'] != "Profile"])

    # Populate albums and artists
    for song in songs_data:
        if not song.get('title') or song.get('title') == "Profile":
            continue

        artist = song.get('artist', 'Unknown Artist')
        album = song.get('album', 'Uncategorized')
        title = song['title']

        # Add to artist list
        if artist not in catalog['artists']:
            catalog['artists'][artist] = []
        catalog['artists'][artist].append(title)

        # Add to album list
        if album not in catalog['albums']:
             catalog['albums'][album] = {
                "artist": artist,
                "songs": []
            }
        catalog['albums'][album]["songs"].append(title)


    # Sort lists for clean output
    for artist in catalog['artists']:
        catalog['artists'][artist].sort()
    for album in catalog['albums']:
        catalog['albums'][album]["songs"].sort()


    filepath = os.path.join(base_path, 'catalog.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)
    print("catalog.json created successfully.")


def process_songbook(input_filepath, output_dir):
    """
    Main function to load the songbook, and create all organized files.
    """
    try:
        print(f"Loading songbook from: {input_filepath}")
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{input_filepath}' is not a valid JSON file.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return

    songs_data = data.get('songs', [])
    # Filter out the profile entry from the main song list for processing
    songs_only = [song for song in songs_data if song.get('title') != "Profile"]


    create_directories(output_dir)
    create_song_files(songs_only, output_dir)
    create_album_files(songs_only, output_dir)
    create_artist_files(songs_only, output_dir)
    create_profile_and_metadata_files(data, output_dir)
    create_catalog_file(songs_only, output_dir)

    print("\nProcessing complete!")
    print(f"All files have been saved in the '{output_dir}' directory.")

if __name__ == '__main__':
    # --- Configuration ---
    # The name of your songbook JSON file
    INPUT_JSON_FILE = 'alex-wilson-songbook-2025-06-17.json'
    # The name of the folder where all the organized files will be saved
    OUTPUT_DIRECTORY = 'alex_wilson_songbook_organized'

    # --- Run the script ---
    process_songbook(INPUT_JSON_FILE, OUTPUT_DIRECTORY)
