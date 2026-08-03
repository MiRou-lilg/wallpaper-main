import os
import re
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Path to your wallpapers folder
FOLDER_PATH = r"D:\wallpapers\0.w.p"

def clean_filename(text):
    """Turns AI text into a clean, safe filename."""
    # Convert to lowercase and replace spaces with underscores
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove special characters
    text = re.sub(r'[\s-]+', '_', text)   # Replace spaces/hyphen with single underscore
    return text[:50]  # Limit length to 50 chars for clean file names

def main():
    print("Loading AI vision model... (this takes a few seconds on first run)")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    files = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith(valid_extensions)]

    if not files:
        print(f"No images found in {FOLDER_PATH}")
        return

    print(f"Found {len(files)} images. Starting renaming process...\n")

    for filename in files:
        old_path = os.path.join(FOLDER_PATH, filename)
        ext = os.path.splitext(filename)[1]

        try:
            # Open image and generate descriptive caption
            raw_image = Image.open(old_path).convert('RGB')
            inputs = processor(raw_image, return_tensors="pt")
            out = model.generate(**inputs, max_new_tokens=20)
            caption = processor.decode(out[0], skip_special_tokens=True)

            # Generate new file name
            base_name = clean_filename(caption)
            if not base_name:
                base_name = "wallpaper"

            new_filename = f"{base_name}{ext}"
            new_path = os.path.join(FOLDER_PATH, new_filename)

            # Avoid overwriting existing files with the same name
            counter = 1
            while os.path.exists(new_path) and new_path != old_path:
                new_filename = f"{base_name}_{counter}{ext}"
                new_path = os.path.join(FOLDER_PATH, new_filename)
                counter += 1

            if old_path != new_path:
                os.rename(old_path, new_path)
                print(f"Renamed: '{filename}' ➔ '{new_filename}'")
            else:
                print(f"Skipped: '{filename}' (already has correct name)")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("\nDone renaming all wallpapers!")

if __name__ == "__main__":
    main()