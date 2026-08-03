import os
import re
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

FOLDER_PATH = r"D:\wallpapers\0.w.p"

# Keyphrase dictionary for auto-categorization
CATEGORIES = {
    "Anime": ["anime", "manga", "illustration", "drawn", "character", "girl", "boy", "art"],
    "Nature": ["mountain", "forest", "tree", "river", "ocean", "beach", "sunset", "sky", "landscape", "flower", "waterfall", "sun", "cloud"],
    "SciFi": ["cyberpunk", "space", "galaxy", "planet", "robot", "futuristic", "sci-fi", "neon", "spaceship", "star"],
    "Architecture": ["building", "city", "street", "house", "bridge", "architecture", "tower", "room"],
    "Vehicles": ["car", "vehicle", "motorcycle", "plane", "airplane", "ship"],
    "Abstract": ["abstract", "pattern", "texture", "minimalist", "vector", "3d", "render", "shape"]
}

def clean_description(text):
    """Clean the raw AI caption for file naming."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove special characters
    text = re.sub(r'[\s-]+', ' ', text)   # Replace multiple spaces with single space
    return text[:40].strip()

def detect_category(caption):
    """Finds matching category based on words in the caption."""
    caption_lower = caption.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in caption_lower:
                return category
    return "General" # Default category if no keywords match

def main():
    if not os.path.exists(FOLDER_PATH):
        print(f"Error: Path '{FOLDER_PATH}' does not exist.")
        return

    print("Loading AI vision model...")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    files = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith(valid_extensions)]

    if not files:
        print("No images found to process.")
        return

    print(f"Found {len(files)} wallpapers. Organizing and numbering...\n")

    for index, filename in enumerate(files, start=1):
        old_path = os.path.join(FOLDER_PATH, filename)
        ext = os.path.splitext(filename)[1].lower()

        try:
            # Generate description using AI
            raw_image = Image.open(old_path).convert('RGB')
            inputs = processor(raw_image, return_tensors="pt")
            out = model.generate(**inputs, max_new_tokens=20)
            caption = processor.decode(out[0], skip_special_tokens=True)

            # Categorize and format details
            category = detect_category(caption)
            description = clean_description(caption)
            if not description:
                description = "wallpaper"

            # Form new filename: Category - Number - Description.ext
            number_str = f"{index:03d}"  # Pads with zeros (001, 002, 010, etc.)
            new_filename = f"{category} - {number_str} - {description}{ext}"
            new_path = os.path.join(FOLDER_PATH, new_filename)

            # Rename file
            os.rename(old_path, new_path)
            print(f"Renamed ({index}/{len(files)}): '{filename}' ➔ '{new_filename}'")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("\nDone organizing all wallpapers!")

if __name__ == "__main__":
    main()