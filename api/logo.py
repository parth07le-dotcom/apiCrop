from http.server import BaseHTTPRequestHandler
import json, os, sys, base64, uuid, urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logo

from vercel_blob import put


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            payload = json.loads(body.decode())

            job = str(uuid.uuid4())
            workdir = f"/tmp/{job}"
            os.makedirs(workdir, exist_ok=True)

            input_path = os.path.join(workdir, "input.pdf")

            # CASE 1: PDF upload
            if "pdf_base64" in payload:
                file_bytes = base64.b64decode(payload["pdf_base64"])
                open(input_path, "wb").write(file_bytes)

            # CASE 2: File URL
            elif "file_url" in payload:
                urllib.request.urlretrieve(payload["file_url"], input_path)

            else:
                raise Exception("No file provided")

            # RUN YOUR LOGIC
            result = logo.run(workdir, input_path)

            # UPLOAD ONLY LOGOS
            logos_dir = os.path.join(workdir, "logos")
            logo_urls = []

            if os.path.exists(logos_dir):
                for f in os.listdir(logos_dir):
                    path = os.path.join(logos_dir, f)
                    with open(path, "rb") as img:
                        blob = put(f"logos/{job}_{f}", img.read(), {"access": "public"})
                        logo_urls.append(blob["url"])

            # KEEP SAME RESPONSE FORMAT
            result["logos"] = logo_urls

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "success": True,
                "data": result
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
