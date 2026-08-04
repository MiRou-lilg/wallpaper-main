import os
import re
import shutil
import colorsys
import hashlib
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# 1. Base Directory Paths
BASE_DIR = r"D:\wallpapers\wallpaper-main\0.w.p"
STAGING_DIR = os.path.join(BASE_DIR, "staging")

# 2. Index Mapping
# Format: "Number": ("Folder Name", "Category Slug", Include Description Tag)
CATEGORY_MAP = {
    "01": ("01-Abstract", "abstract", False),
    "02": ("02-anime girl", "anime-girl", False),
    "03": ("03-anime art", "anime-art", True),
    "04": ("04-cyber-neon", "cyberneon", False),
    "05": ("05-fantasy", "fantasy", False),
    "06": ("06-nature-city", "nature-city", False),
    "07": ("07-room-window", "room-window", False),
    "08": ("08-sky", "sky", False),
    "09": ("09-space", "space", False),
    "10": ("10-visula art", "visual-art", False),
    "11": ("11-other", "other", True)
}


def brighten_hex(hexcode: str) -> str:
    """
    Takes a raw extracted hex color (no '#') and returns a punchier,
    more UI-visible version: saturation pushed up to at least ~65%,
    lightness clamped into a ~46-62% vivid band. Near-grayscale /
    near-black / near-white inputs (no real hue to boost) instead get
    a deterministic vivid neon hue derived from that exact hex, so
    every wallpaper still ends up with its own distinct strong color
    instead of a generic fallback.
    """
    clean_hex = hexcode.strip().lstrip('#').lower()
    if len(clean_hex) != 6:
        return hexcode

    r = int(clean_hex[0:2], 16) / 255
    g = int(clean_hex[2:4], 16) / 255
    b = int(clean_hex[4:6], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    if s < 0.18:
        seed = int(hashlib.md5(clean_hex.encode()).hexdigest(), 16)
        h = (seed % 360) / 360
        s = 0.80
        l = 0.56
    else:
        s = min(1.0, max(s * 1.45, 0.65))
        l = min(0.62, max(l, 0.46))

    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return "%02x%02x%02x" % (round(r2 * 255), round(g2 * 255), round(b2 * 255))


def extract_main_colors(image_path, num_colors=2):
    """Extracts top 2 dominant colors from an image, already converted
    to their final vivid/UI-ready HEX form."""
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

            raw_hexes = [f"{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors]
            return [f"#{brighten_hex(h)}" for h in raw_hexes]
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
        print("Put your files inside 'staging' named like: '01.jpg' or '03 -d- neon_art.png'")
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

        # Parse folder index and optional description
        if "-d-" in name_without_ext:
            parts = name_without_ext.split("-d-", 1)
            raw_index = parts[0].strip()
            description = parts[1].strip()
        else:
            raw_index = name_without_ext.strip()
            description = ""

        # Format number to 2 digits (e.g., "1" -> "01")
        formatted_key = raw_index.zfill(2)

        # Target category resolution
        if formatted_key in CATEGORY_MAP:
            target_folder, cat_slug, include_desc = CATEGORY_MAP[formatted_key]
        else:
            print(f"⚠️ Index key '{raw_index}' not recognized. Defaulting to '11-other'.")
            target_folder, cat_slug, include_desc = CATEGORY_MAP["11"]
            description = description if description else raw_index

        target_dir_path = os.path.join(BASE_DIR, target_folder)
        os.makedirs(target_dir_path, exist_ok=True)

        # Get next file index inside target directory
        next_index = get_next_sequence_number(target_dir_path)
        num_prefix = f"{next_index:02d}"

        # Extract dominant colors — already returned in final vivid/UI-ready form
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