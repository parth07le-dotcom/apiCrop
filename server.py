from flask import Flask, request, jsonify, send_from_directory
import os
import base64
import uuid
import logo
import json

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api/logo', methods=['POST'])
def api_logo():
    try:
        payload = request.json
        job = str(uuid.uuid4())
        
        # Use a temporary directory for processing
        workdir = os.path.join(BASE_DIR, "temp_uploads", job)
        os.makedirs(workdir, exist_ok=True)
        
        input_path = os.path.join(workdir, "input.pdf")

        # Handle Base64 Upload
        if "pdf_base64" in payload:
            # Remove header if present (e.g., "data:application/pdf;base64,")
            b64_data = payload["pdf_base64"]
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
                
            file_bytes = base64.b64decode(b64_data)
            with open(input_path, "wb") as f:
                f.write(file_bytes)
                
        elif "file_url" in payload:
             # For local dev, we might just mock this or support it if needed
             return jsonify({"success": False, "error": "URL processing not fully supported deeply in local mode yet, please upload file"})
        else:
            return jsonify({"success": False, "error": "No file provided"})

        print(f"Processing job {job}, saving to {workdir}")
        print(f"Input path: {input_path}")

        # Run extraction
        print("Calling logo.extract_all_images...")
        result = logo.extract_all_images(workdir, input_path)
        print(f"Extraction result: {result}")
        
        if "error" in result:
             return jsonify({"success": False, "error": result["error"]})

        # The extract_all_images returns "output_dir" where logos are
        logos_dir = result["output_dir"]
        logo_urls = []
        
        if os.path.exists(logos_dir):
            for f in os.listdir(logos_dir):
                # Construct a local URL for the image
                # We need to serve this directory. 
                # Let's assume we serve "temp_uploads" via a static route.
                # URL format: /temp_uploads/<job>/logos/<filename>
                logo_urls.append(f"/temp_uploads/{job}/logos/{f}")

        return jsonify({
            "success": True,
            "data": {
                "logos": logo_urls,
                "count": len(logo_urls)
            }
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/images', methods=['GET'])
def get_all_images():
    """
    Scans temp_uploads for all images and returns them grouped by job ID (category).
    """
    temp_dir = os.path.join(BASE_DIR, "temp_uploads")
    assets = {}

    if not os.path.exists(temp_dir):
        return jsonify({})

    # Walk through all jobs
    for job_id in os.listdir(temp_dir):
        job_path = os.path.join(temp_dir, job_id)
        if not os.path.isdir(job_path):
            continue

        # Check for 'logos' folder inside the job
        logos_path = os.path.join(job_path, "logos")
        if os.path.exists(logos_path) and os.path.isdir(logos_path):
            images = []
            for f in os.listdir(logos_path):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # Use the same serving path convention
                    images.append(f)
            
            if images:
                assets[job_id] = images

    return jsonify(assets)

@app.route('/temp_uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(os.path.join(BASE_DIR, "temp_uploads"), filename)

# Moved to the bottom to avoid shadowing other routes
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(BASE_DIR, path)

if __name__ == '__main__':
    print("Starting local server at http://localhost:5000")
    print("Serving from:", BASE_DIR)
    app.run(debug=True, port=5000)
