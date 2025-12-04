import requests

print("Testing Flask routes...")

base = "http://127.0.0.1:5000"

tests = [
    "/",
    "/index.html",
    "/intro.html",
    "/script.js",
    "/api/config"
]

for path in tests:
    try:
        url = base + path
        response = requests.get(url, timeout=5)
        print(f"{path:30} -> {response.status_code}")
    except Exception as e:
        print(f"{path:30} -> ERROR: {e}")
