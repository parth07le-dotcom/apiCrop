import os
import json

def generate_gallery(assets_dir="assets", gallery_file="gallery.html"):
    if not os.path.exists(assets_dir):
        print(f"Warning: {assets_dir} not found.")
        return

    assets = {}
    
    # Walk through the assets directory
    for root, dirs, files in os.walk(assets_dir):
        # Skip the root assets directory itself if it yields files directly, 
        # but we also want to catch subdirectories.
        # If we just put files in 'extracted' subfolder, we can just grab that.
        
        rel_path = os.path.relpath(root, assets_dir)
        if rel_path == ".": continue

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
        # We need a template or we just overwrite. 
        # Since we are on Vercel, we can't easily modify the source 'gallery.html' and expect it to persist or be served easily if it's static.
        # But for the API response, we might just want the JSON data?
        # Or if we want to write the file to /tmp for checking.
        
        # For now, let's just write to the target file if it exists, or create a simple one if not.
        
        if os.path.exists(gallery_file):
            with open(gallery_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            found = False
            for line in lines:
                if line.strip().startswith("const assets ="):
                    new_lines.append(f"        const assets = {json.dumps(assets_sorted)};\n")
                    found = True
                else:
                    new_lines.append(line)
            
            if not found:
                 # Minimal fallback if line not found
                 pass 

            with open(gallery_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        else:
            # Create minimal file if missing (useful for /tmp)
            with open(gallery_file, 'w', encoding='utf-8') as f:
                f.write(f"<script>const assets = {json.dumps(assets_sorted)};</script>")

        print(f"Updated {gallery_file} with {sum(len(v) for v in assets.values())} assets.")

    except Exception as e:
        print(f"Error updating gallery: {e}")

if __name__ == "__main__":
    generate_gallery()
