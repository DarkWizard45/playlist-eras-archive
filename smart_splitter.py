import json
import os
from pathlib import Path
import re

def make_safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# === SETTINGS ===
BASE_DIR = Path(__file__).resolve().parent

# INPUT_WAVE_FILE = BASE_DIR / "docs" / "static" / "data" / "PostNeural_Bloom_2022-2024.json"
WAVE_PLAYLIST_MAP_FILE = BASE_DIR / "docs" / "static" / "data" / "wave_playlist_map.json"
OUTPUT_BASE_FOLDER = BASE_DIR / "docs" / "static" / "data" / "split_output"

# Helper function to load JSON
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Helper function to save JSON
def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Main logic
def smart_split_wave(input_wave_file, wave_playlist_map_file, output_base_folder):
    wave_data = load_json(input_wave_file)
    wave_playlist_map = load_json(wave_playlist_map_file)

    filename = os.path.basename(input_wave_file)
    wave_name = None

    for name, details in wave_playlist_map.items():
        if details['file'] == filename:
            wave_name = name
            expected_playlists = set(details['playlists'])
            break

    if not wave_name:
        raise ValueError(f"Could not find wave mapping for {filename}")

    print(f"Splitting {wave_name}...")

    playlist_groups = {pl: [] for pl in expected_playlists}

    for playlist in wave_data.get('playlists', []):
        name = playlist.get('name', '').strip()
        if name in expected_playlists:
            playlist_groups[name].extend(playlist.get('items', []))

    for playlist_name, tracks in playlist_groups.items():
        if not tracks:
            continue
        safe_name = make_safe_filename(playlist_name.strip().replace(' ', '_'))
        output_file = os.path.join(
            output_base_folder,
            make_safe_filename(wave_name.strip().replace(' ', '_')),
            f"{safe_name}.json"
        )
        save_json(tracks, output_file)
        print(f"✅ Saved {len(tracks)} tracks to {output_file}")


import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_splitter.py <input_wave_file>")
        sys.exit(1)

    input_file_arg = Path(sys.argv[1])
    smart_split_wave(input_file_arg, WAVE_PLAYLIST_MAP_FILE, OUTPUT_BASE_FOLDER)