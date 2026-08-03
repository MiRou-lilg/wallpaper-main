import os
import re
import shutil
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# 1. Base Directory Paths
BASE_DIR = r"D:\wallpapers\wallpaper-main\0.w.p"
STAGING_DIR = os.path.join(BASE_DIR, "staging")

# 2. Strict Mapping for Categories
# Keys: What you write in the filename before '-d-' or as the filename
# Values: (Destination Folder Name, Prefix, Include Description Tag)
CATEGORY_MAP = {
    "abstract": ("Abstract", "01-abstract", False),
    "anime girl": ("anime girl", "01-anime-girl", False),
    "anime art": ("anime-stylish color art", "01-anime-art", True),
    "cyberneon": ("cyber-neon", "01-cyberneon", False),
    "fantasy": ("fnatasy", "01-fantasy", False),
    "nature city": ("nature-city-animal", "01-nature-city", False),
    "room window": ("room-window", "01-room-window", False),
    "sky": ("sky", "01-sky", False),
    "space": ("space", "01-space", False),
    "visual art": ("visula art", "01-visual-art", False),
    "other": ("other", "01-other", True)
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

def process_staging():
    if not os.path.exists(STAGING_DIR):
        os.makedirs(STAGING_DIR)
        print(f"Created staging folder at: {STAGING_DIR}")
        print("Put your files inside 'staging' named like: 'abstract.jpg' or 'anime art -d- my_art.png'")
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

        # Parse category and optional description from filename
        # Expected format: "category" OR "category -d- description"
        if "-d-" in name_without_ext:
            parts = name_without_ext.split("-d-", 1)
            raw_cat = parts[0].strip().lower()
            description = parts[1].strip()
        else:
            raw_cat = name_without_ext.strip().lower()
            description = ""

        # Normalize category name separators (underscores/dashes to spaces)
        raw_cat_clean = re.sub(r'[\-_]', ' ', raw_cat).strip()

        # Route file based on your input
        if raw_cat_clean in CATEGORY_MAP:
            target_folder, cat_prefix, include_desc = CATEGORY_MAP[raw_cat_clean]
        else:
            # Fallback if category name isn't recognized
            print(f"⚠️ Category '{raw_cat}' not recognized for file '{file_name}'. Defaulting to 'other'.")
            target_folder, cat_prefix, include_desc = CATEGORY_MAP["other"]
            description = description if description else raw_cat

        # Destination Folder Path
        target_dir_path = os.path.join(BASE_DIR, target_folder)
        os.makedirs(target_dir_path, exist_ok=True)

        # Extract 2 main colors
        c1, c2 = extract_main_colors(file_path, num_colors=2)
        color_str = f"({c1},{c2})"

        # Construct final name strictly according to your rules
        if include_desc:
            if description:
                new_filename = f"{cat_prefix}-d-{description}-{color_str}{ext}"
            else:
                new_filename = f"{cat_prefix}-d-{color_str}{ext}"
        else:
            new_filename = f"{cat_prefix}-{color_str}{ext}"

        # Prevent file overwrites
        destination_path = os.path.join(target_dir_path, new_filename)
        counter = 1
        while os.path.exists(destination_path):
            if include_desc and description:
                new_filename = f"{cat_prefix}-d-{description}_{counter}-{color_str}{ext}"
            elif include_desc:
                new_filename = f"{cat_prefix}-d_{counter}-{color_str}{ext}"
            else:
                new_filename = f"{cat_prefix}_{counter}-{color_str}{ext}"
            destination_path = os.path.join(target_dir_path, new_filename)
            counter += 1

        # Move file from staging to destination folder
        shutil.move(file_path, destination_path)
        print(f"Routed: {file_name}  -->  [{target_folder}]\\{new_filename}")

    print("\nStaging processing complete!")

if __name__ == "__main__":
    process_staging()