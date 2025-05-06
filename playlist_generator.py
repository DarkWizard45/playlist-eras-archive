import os
import sys
import json
import openai  # Optional: can be removed if not using GPT at all
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-modify-public"
))

def load_songs_from_file(file_path):
    songs = []

    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            songs = json.load(f)

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if '-' in line:
                    parts = line.strip().split('-')
                    if len(parts) >= 2:
                        songs.append({
                            "artist": parts[0].strip(),
                            "title": parts[1].strip()
                        })

    else:
        print("Unsupported file type. Use .txt or .json.")
        sys.exit(1)

    return songs

def search_track(song):
    query = f"{song['title']} {song['artist']}"
    results = sp.search(q=query, type='track', limit=1)
    items = results.get('tracks', {}).get('items', [])
    return items[0]['uri'] if items else None

def create_playlist(name, track_uris):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True)
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
    return playlist['external_urls']['spotify']

def main():
    if len(sys.argv) < 2:
        print("Usage: python playlist_generator.py <filename>")
        sys.exit(1)

    file_path = sys.argv[1]
    playlist_name = os.path.splitext(os.path.basename(file_path))[0]
    songs = load_songs_from_file(file_path)

    print(f"🎧 Searching Spotify for {len(songs)} songs from: {file_path}")

    uris = []
    failed = []

    for song in songs:
        uri = search_track(song)
        if uri:
            uris.append(uri)
        else:
            failed.append(song)

    print(f"\n✅ Matched {len(uris)} tracks. ❌ {len(failed)} unmatched.")
    playlist_url = create_playlist(name=playlist_name, track_uris=uris)
    print(f"\n🎵 Playlist created: {playlist_url}")

    # Save a summary
    summary_file = f"{playlist_name}_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"Playlist name: {playlist_name}\n")
        f.write(f"Playlist URL: {playlist_url}\n\n")
        f.write("Tracklist:\n")
        for song in songs:
            f.write(f"{song['artist']} - {song['title']}\n")
        if failed:
            f.write("\nUnmatched Songs:\n")
            for song in failed:
                f.write(f"{song['artist']} - {song['title']}\n")

    print(f"📝 Summary saved to {summary_file}")

if __name__ == "__main__":
    main()