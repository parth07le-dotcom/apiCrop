import os
import json

ASSETS_DIR = "assets"
GALLERY_FILE = "gallery.html"

def generate_gallery():
    if not os.path.exists(ASSETS_DIR):
        print(f"Warning: {ASSETS_DIR} not found.")
        return

    assets = {}
    
    # Walk through the assets directory
    for root, dirs, files in os.walk(ASSETS_DIR):
        # Skip the root assets directory itself, we want subdirectories
        if os.path.normpath(root) == os.path.normpath(ASSETS_DIR):
            continue
            
        category = os.path.basename(root)
        
        # Filter for image files
        image_files = [
            f for f in files 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
        ]
        image_files.sort()
        
        if image_files:
            assets[category] = image_files

    # Sort categories alphabetically
    assets_sorted = {k: assets[k] for k in sorted(assets)}

    try:
        # Read the existing HTML file
        with open(GALLERY_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Replace the assets data
        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith("const assets ="):
                new_lines.append(f"        const assets = {json.dumps(assets_sorted)};\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            print("Error: Could not find 'const assets =' line in gallery.html")
            # If not found, one might want to append it or handle it, 
            # but for now we assume the structure is intact.
            return

        # Write back the updated HTML
        with open(GALLERY_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        total_images = sum(len(v) for v in assets.values())
        print(f"Updated {GALLERY_FILE} with {total_images} assets across {len(assets)} categories.")

    except FileNotFoundError:
        print(f"Error: {GALLERY_FILE} not found.")
    except Exception as e:
        print(f"Error updating gallery: {e}")

if __name__ == "__main__":
    generate_gallery()
