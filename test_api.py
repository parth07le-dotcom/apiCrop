import requests
import base64

url = "http://localhost:5000/api/logo"
headers = {"Content-Type": "application/json"}
data = {
    "pdf_base64": "data:application/pdf;base64," + base64.b64encode(b"Dummy PDF Content").decode('utf-8')
}

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
