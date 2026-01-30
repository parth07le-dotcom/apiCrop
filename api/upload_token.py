from http.server import BaseHTTPRequestHandler
import json
from vercel_blob import create_upload_url

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            upload_url = create_upload_url({
                "access": "public",
                "contentType": "application/pdf"
            })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "uploadUrl": upload_url
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "error": str(e)
            }).encode())
