```python
import requests

BASE_URL = "http://127.0.0.1:8000" # The base URL of the shop service

if __name__ == "__main__":
    response = requests.get(f"{BASE_URL}/ping")
    try:
        response.raise_for_status() # Raise an error for bad responses
        print("Shop service says:", response.text)
    except requests.exceptions.HTTPError as e:
        print("Error contacting the shop service:", e)
        exit(1)
