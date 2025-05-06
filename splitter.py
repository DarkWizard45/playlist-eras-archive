import json
import os

def split_json(input_file, output_base_folder, max_entries_per_file=500):
    # Extract base name (e.g., Delta_Drift_Wave)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Create a subfolder for this Wave
    wave_folder = os.path.join(output_base_folder, base_name)
    os.makedirs(wave_folder, exist_ok=True)

    # Load the large JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Confirm it's a list
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of entries (tracks).")

    total_entries = len(data)
    print(f"Total entries found: {total_entries}")

    # Split into chunks
    for i in range(0, total_entries, max_entries_per_file):
        chunk = data[i:i + max_entries_per_file]
        chunk_number = i // max_entries_per_file + 1

        # Build output file path inside the Wave subfolder
        output_file = os.path.join(wave_folder, f"{base_name}_part{chunk_number}.json")

        # Save the chunk
        with open(output_file, 'w', encoding='utf-8') as f_out:
            json.dump(chunk, f_out, indent=2, ensure_ascii=False)

        print(f"Saved {len(chunk)} entries to {output_file}")

    print("Splitting complete.")

if __name__ == "__main__":
    # === SETTINGS ===
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent
    INPUT_FILE = BASE_DIR / "static" / "data" / "Delta_Drift_Wave_Dummy.json"
    OUTPUT_BASE_FOLDER = BASE_DIR / "static" / "data" / "split_output"
    MAX_ENTRIES = 3

    split_json(INPUT_FILE, OUTPUT_BASE_FOLDER, MAX_ENTRIES)