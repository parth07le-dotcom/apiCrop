import fitz  # pymupdf
import os
import hashlib
import gallery_generator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_PATH = os.path.join(BASE_DIR, "FINAL Brand Guidelines 10.29.19.pdf")
OUTPUT = os.path.join(BASE_DIR, "assets")

def extract_all_images():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF not found at {PDF_PATH}")
        return 0

    try:
        doc = fitz.open(PDF_PATH)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return 0

    seen = set()
    saved = 0

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    for page_i in range(len(doc)):
        page = doc[page_i]
        images = page.get_images(full=True)

        for img_i, img_info in enumerate(images):
            xref = img_info[0]
            base = doc.extract_image(xref)
            data = base["image"]
            ext = base["ext"]

            h_hash = hashlib.md5(data).hexdigest()
            if h_hash in seen:
                continue
            seen.add(h_hash)

            name = f"page{page_i+1}_{img_i}.{ext}"
            
            # Save directly to OUTPUT (or organize into subfolders if preferred, 
            # but original code put them in subfolders like 'others' via classify_image which is now gone.
            # For now, let's just put them in 'assets/extracted' to keep them separate 
            # or directly in assets. The gallery generator expects subfolders.
            # The previous code had 'output/category/name'. 
            # The user asked to remove "unnecessary code". 
            # Without classify_image, we can't sort them.
            # Let's put them all in a folder named 'extracted'.
            
            target_dir = os.path.join(OUTPUT, "extracted")
            os.makedirs(target_dir, exist_ok=True)
            
            path = os.path.join(target_dir, name)

            with open(path, "wb") as f:
                f.write(data)

            saved += 1

    return saved

def run():
    extracted_count = extract_all_images()
    gallery_generator.generate_gallery()

    return {
        "pdf_images_extracted": extracted_count,
        "status": "completed"
    }

if __name__ == "__main__":
    print(run())
