import os
import hashlib

# Path to your wallpapers folder
FOLDER_PATH = r"D:\wallpapers\0.w.p"

def get_file_hash(filepath, chunk_size=8192):
    """Calculates MD5 hash of a file to check for identical file contents."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Could not read {filepath}: {e}")
        return None

def remove_duplicates():
    if not os.path.exists(FOLDER_PATH):
        print(f"Error: Folder '{FOLDER_PATH}' does not exist.")
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')
    seen_hashes = {}
    duplicates_deleted = 0
    total_files = 0

    print(f"Scanning '{FOLDER_PATH}' for duplicates...\n")

    for root, _, files in os.walk(FOLDER_PATH):
        for filename in files:
            if filename.lower().endswith(valid_extensions):
                total_files += 1
                filepath = os.path.join(root, filename)
                file_hash = get_file_hash(filepath)

                if not file_hash:
                    continue

                if file_hash in seen_hashes:
                    # Duplicate found! Keep the original, delete this copy
                    original_file = seen_hashes[file_hash]
                    try:
                        os.remove(filepath)
                        duplicates_deleted += 1
                        print(f"Deleted duplicate: '{filename}' ➔ (Original: '{os.path.basename(original_file)}')")
                    except Exception as e:
                        print(f"Failed to delete {filename}: {e}")
                else:
                    # First time seeing this hash, store it
                    seen_hashes[file_hash] = filepath

    print("\n--- Summary ---")
    print(f"Total images checked: {total_files}")
    print(f"Duplicates removed: {duplicates_deleted}")
    print(f"Unique images remaining: {len(seen_hashes)}")

if __name__ == "__main__":
    remove_duplicates()