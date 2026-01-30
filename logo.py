import fitz  # pymupdf
import os
import hashlib
import gallery_generator

# Defaults for local testing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PDF = os.path.join(BASE_DIR, "2016-CMOC-Brand-ID-10-3-16.pdf")

def extract_all_images(output_dir, pdf_path):
    if not os.path.exists(pdf_path):
        return {"error": f"PDF not found at {pdf_path}"}

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"error": f"Error opening PDF: {e}"}

    seen = set()
    saved = 0

    target_dir = os.path.join(output_dir, "extracted") # Keep all extractions here
    logos_dir = os.path.join(output_dir, "logos") # Specific folder for logos if we had logic
    # Since we removed the specific 'logos' logic, we just save everything to 'extracted' or 'logos' as per user intent?
    # The user API expects 'logos' folder: `logos_dir = os.path.join(workdir, "logos")`
    # But `logo.py` currently only extracts *all* images.
    # We should save to 'logos' for now so the API picks them up, 
    # OR we rename 'extracted' to 'logos' in the API.
    # Let's save to `logos` to match the API expectation effectively.
    
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(logos_dir, exist_ok=True)

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
            
            # Save to 'logos' folder as well/instead so the API finds them?
            # The user API iterates `workdir/logos`.
            # Let's save to `logos` directory.
            path = os.path.join(logos_dir, name)

            with open(path, "wb") as f:
                f.write(data)

            saved += 1

    return {"saved_count": saved, "output_dir": logos_dir}

def run(output_base_dir=None, input_pdf_path=None):
    if output_base_dir is None:
        output_base_dir = os.path.join(BASE_DIR, "assets")
        
    if input_pdf_path is None:
        input_pdf_path = DEFAULT_PDF
        
    result = extract_all_images(output_base_dir, input_pdf_path)
    
    if "error" in result:
        return result
        
    # Generate gallery just for compatibility or debugging
    gallery_file = os.path.join(output_base_dir, "gallery_generated.html")
    gallery_generator.generate_gallery(output_base_dir, gallery_file)

    return {
        "pdf_images_extracted": result["saved_count"],
        "gallery": gallery_file,
        "status": "completed"
    }

if __name__ == "__main__":
    print(run())
