import os
import re
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# 1. Base Directory
BASE_DIR = r"D:\wallpapers\0.w.p"

# 2. Folder to Category Mapping
FOLDER_MAP = {
    "abstract": ("01-abstract", False),
    "anime girl": ("01-anime-girl", False),
    "anime-stylish color art": ("01-anime-art", True),
    "cyber-neon": ("01-cyberneon", False),
    "fnatasy": ("01-fantasy", False),
    "fantasy": ("01-fantasy", False),
    "lofi-night-low-chill": ("01-other", True),
    "nature-city-animal": ("01-nature-city", False),
    "other": ("01-other", True),
    "room-window": ("01-room-window", False),
    "sky": ("01-sky", False),
    "space": ("01-space", False),
    "visula art": ("01-visual-art", False),
    "visual art": ("01-visual-art", False)
}

def extract_main_colors(image_path, num_colors=2):
    """Extracts top dominant colors from an image in HEX format."""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img.thumbnail((150, 150)) # Resize for faster processing
            img_data = np.array(img).reshape(-1, 3)
            
            # Use KMeans to group colors into 2 main clusters
            kmeans = KMeans(n_clusters=num_colors, n_init=5, random_state=42)
            kmeans.fit(img_data)
            
            # Sort colors by frequency/presence
            labels, counts = np.unique(kmeans.labels_, return_counts=True)
            sorted_indices = np.argsort(-counts)
            dominant_colors = kmeans.cluster_centers_[sorted_indices].astype(int)
            
            # Convert RGB to HEX format (e.g. #FF0055)
            hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors]
            return hex_colors
    except Exception as e:
        print(f"Error reading color for {image_path}: {e}")
        return ["#000000", "#ffffff"]

def clean_description(filename):
    """Cleans existing filenames to isolate description if needed."""
    name, _ = os.path.splitext(filename)
    # Remove numbers or existing hex codes if present
    name = re.sub(r'^\d+[\s\-_]*', '', name)
    name = re.sub(r'\([#\w,\s\-_]+\)', '', name)
    name = name.strip(" -_")
    return name

def rename_wallpapers():
    if not os.path.exists(BASE_DIR):
        print(f"Directory {BASE_DIR} does not exist!")
        return

    for folder_name in os.listdir(BASE_DIR):
        folder_path = os.path.join(BASE_DIR, folder_name)
        
        # Ensure we only process directories (don't merge or move folders)
        if not os.path.isdir(folder_path):
            continue

        folder_key = folder_name.lower().strip()
        
        # Match target folder settings
        if folder_key in FOLDER_MAP:
            cat_prefix, include_desc = FOLDER_MAP[folder_key]
        else:
            cat_prefix, include_desc = ("01-other", True)

        print(f"\nProcessing Folder: [{folder_name}] -> Target Category: [{cat_prefix}]")

        # Process each file in the subfolder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            
            if not os.path.isfile(file_path):
                continue
            
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                continue

            # Get 2 main colors in HEX
            c1, c2 = extract_main_colors(file_path, num_colors=2)
            color_str = f"({c1},{c2})"

            # Construct new filename strictly per rules
            if include_desc:
                desc = clean_description(file_name)
                if desc:
                    new_filename = f"{cat_prefix}-d-{desc}-{color_str}{ext}"
                else:
                    new_filename = f"{cat_prefix}-d-{color_str}{ext}"
            else:
                new_filename = f"{cat_prefix}-{color_str}{ext}"

            new_filepath = os.path.join(folder_path, new_filename)
            
            # Avoid overwriting identical filenames
            counter = 1
            while os.path.exists(new_filepath) and new_filepath != file_path:
                if include_desc:
                    new_filename = f"{cat_prefix}-d-{desc}_{counter}-{color_str}{ext}"
                else:
                    new_filename = f"{cat_prefix}_{counter}-{color_str}{ext}"
                new_filepath = os.path.join(folder_path, new_filename)
                counter += 1

            # Rename file in place
            os.rename(file_path, new_filepath)
            print(f"Renamed: {file_name}  -->  {new_filename}")

if __name__ == "__main__":
    rename_wallpapers()