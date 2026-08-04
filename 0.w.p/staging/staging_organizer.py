import os
import re
import shutil
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# 1. Base Directory Paths
BASE_DIR = r"D:\wallpapers\wallpaper-main\0.w.p"
STAGING_DIR = os.path.join(BASE_DIR, "staging")

# 2. Category Mapping
# Format: "key": ("Folder Name", "Category Slug", Include Description Tag)
CATEGORY_MAP = {
    "abstract": ("Abstract", "abstract", False),
    "anime girl": ("anime girl", "anime-girl", False),
    "anime art": ("anime-stylish color art", "anime-art", True),
    "cyberneon": ("cyber-neon", "cyberneon", False),
    "fantasy": ("fantasy", "fantasy", False),
    "nature city": ("nature-city-animal", "nature-city", False),
    "room window": ("room-window", "room-window", False),
    "sky": ("sky", "sky", False),
    "space": ("space", "space", False),
    "visual art": ("visual art", "visual-art", False),
    "other": ("other", "other", True)
}

def extract_main_colors(image_path, num_colors=2):
    """Extracts top 2 dominant colors from an image in HEX format."""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img.thumbnail((150, 150))
            img_data = np.array(img).reshape(-1, 3)
            
            kmeans = KMeans(n_clusters=num_colors, n_init=5, random_state=42)
            kmeans.fit(img_data)
            
            labels, counts = np.unique(kmeans.labels_, return_counts=True)
            sorted_indices = np.argsort(-counts)
            dominant_colors = kmeans.cluster_centers_[sorted_indices].astype(int)
            
            return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors]
    except Exception as e:
        print(f"Error extracting colors from {image_path}: {e}")
        return ["#000000", "#ffffff"]

def get_next_sequence_number(target_dir_path):
    """Scans target folder and finds the highest leading number to compute next sequence index."""
    if not os.path.exists(target_dir_path):
        return 1
        
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    max_num = 0
    
    for fname in os.listdir(target_dir_path):
        if os.path.isfile(os.path.join(target_dir_path, fname)) and fname.lower().endswith(valid_extensions):
            match = re.match(r"^(\d+)", fname)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
                    
    return max_num + 1

def process_staging():
    if not os.path.exists(STAGING_DIR):
        os.makedirs(STAGING_DIR)
        print(f"Created staging folder at: {STAGING_DIR}")
        print("Put your files inside 'staging' named like: 'space.jpg' or 'anime art -d- my_art.png'")
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    image_files = [f for f in os.listdir(STAGING_DIR) 
                   if os.path.isfile(os.path.join(STAGING_DIR, f)) and f.lower().endswith(valid_extensions)]

    if not image_files:
        print("No new image files found in staging.")
        return

    print(f"Processing {len(image_files)} image(s) from staging...\n")

    for file_name in image_files:
        file_path = os.path.join(STAGING_DIR, file_name)
        name_without_ext, ext = os.path.splitext(file_name)

        # Parse category and optional description
        if "-d-" in name_without_ext:
            parts = name_without_ext.split("-d-", 1)
            raw_cat = parts[0].strip().lower()
            description = parts[1].strip()
        else:
            raw_cat = name_without_ext.strip().lower()
            description = ""

        raw_cat_clean = re.sub(r'[\-_]', ' ', raw_cat).strip()

        # Target category resolution
        if raw_cat_clean in CATEGORY_MAP:
            target_folder, cat_slug, include_desc = CATEGORY_MAP[raw_cat_clean]
        else:
            print(f"⚠️ Category '{raw_cat}' not recognized. Defaulting to 'other'.")
            target_folder, cat_slug, include_desc = CATEGORY_MAP["other"]
            description = description if description else raw_cat

        target_dir_path = os.path.join(BASE_DIR, target_folder)
        os.makedirs(target_dir_path, exist_ok=True)

        # Get next index (e.g., 39 if highest is 38)
        next_index = get_next_sequence_number(target_dir_path)
        num_prefix = f"{next_index:02d}"

        # Extract dominant colors
        c1, c2 = extract_main_colors(file_path, num_colors=2)
        color_str = f"({c1},{c2})"

        # Build dynamic output filename
        if include_desc and description:
            new_filename = f"{num_prefix}-{cat_slug}-d-{description}-{color_str}{ext}"
        elif include_desc:
            new_filename = f"{num_prefix}-{cat_slug}-d-{color_str}{ext}"
        else:
            new_filename = f"{num_prefix}-{cat_slug}-{color_str}{ext}"

        destination_path = os.path.join(target_dir_path, new_filename)

        # Move file to destination folder
        shutil.move(file_path, destination_path)
        print(f"Routed: {file_name}  -->  [{target_folder}]\\{new_filename}")

    print("\nStaging processing complete!")

if __name__ == "__main__":
    process_staging()