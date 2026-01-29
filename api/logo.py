from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import base64

# Allow importing from root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logo  # root logo.py


def collect_all_images_as_base64(base_folder):
    images = []

    if not os.path.exists(base_folder):
        return images

    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(root, file)
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")

                images.append({
                    "name": file,
                    "folder": root.replace(base_folder, ""),
                    "data_url": f"data:image/png;base64,{encoded}"
                })

    return images


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Vercel only allows writing to /tmp
            output_dir = "/tmp/assets"
            os.makedirs(output_dir, exist_ok=True)

            # Run your main logic
            result = logo.run(output_dir)

            # Collect ALL images recursively
            images = collect_all_images_as_base64(output_dir)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "success": True,
                "data": result,
                "total_images": len(images),
                "images": images
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())

    def do_POST(self):
        return self.do_GET()
