import fitz  # pymupdf
import os
import hashlib
import gallery_generator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "FINAL Brand Guidelines 10.29.19.pdf")

def extract_all_images(output_dir):
    if not os.path.exists(PDF_PATH):
        return {"error": f"PDF not found at {PDF_PATH}"}

    try:
        doc = fitz.open(PDF_PATH)
    except Exception as e:
        return {"error": f"Error opening PDF: {e}"}

    seen = set()
    saved = 0

    target_dir = os.path.join(output_dir, "extracted")
    os.makedirs(target_dir, exist_ok=True)

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
            path = os.path.join(target_dir, name)

            with open(path, "wb") as f:
                f.write(data)

            saved += 1

    return {"saved_count": saved, "output_dir": target_dir}

def run(output_base_dir=None):
    if output_base_dir is None:
        output_base_dir = os.path.join(BASE_DIR, "assets")
        
    result = extract_all_images(output_base_dir)
    
    if "error" in result:
        return result
        
    gallery_file = os.path.join(output_base_dir, "gallery_generated.html")
    gallery_generator.generate_gallery(output_base_dir, gallery_file)

    return {
        "pdf_images_extracted": result["saved_count"],
        "gallery": gallery_file,
        "status": "completed"
    }

if __name__ == "__main__":
    print(run())
