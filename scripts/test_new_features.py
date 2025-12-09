import requests
import io

API_URL = "http://localhost:8000"

def test_chat():
    print("Testing Chat...")
    try:
        res = requests.post(f"{API_URL}/chat/", json={"query": "How many providers?"})
        print(f"Chat Response: {res.json()}")
    except Exception as e:
        print(f"Chat Failed: {e}")

def test_upload():
    print("\nTesting CSV Upload...")
    csv_content = "npi,first_name,last_name\n1234567890,Test,User"
    file = {'file': ('test.csv', io.StringIO(csv_content), 'text/csv')}
    try:
        res = requests.post(f"{API_URL}/upload-csv/", files=file)
        print(f"Upload Response: {res.json()}")
    except Exception as e:
        print(f"Upload Failed: {e}")

if __name__ == "__main__":
    test_chat()
    test_upload()
