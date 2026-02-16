import urllib.request
import json

def test_api():
    base_url = "http://127.0.0.1:8000"

    print("Testing API Endpoints...")
    print("=" * 50)

    # Test 1: Root endpoint
    print("\n1. Testing GET /")
    try:
        req = urllib.request.Request(f"{base_url}/")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"   Status: OK")
            print(f"   Name: {data.get('name')}")
            print(f"   Status: {data.get('status')}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Health check
    print("\n2. Testing GET /health")
    try:
        req = urllib.request.Request(f"{base_url}/health")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"   Status: {data}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: Stock list
    print("\n3. Testing GET /api/stocks/list")
    try:
        req = urllib.request.Request(f"{base_url}/api/stocks/list")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"   Status: OK")
            print(f"   Total stocks: {data.get('data', {}).get('total', 0)}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 4: Stock scores
    print("\n4. Testing GET /api/stocks/scores")
    try:
        req = urllib.request.Request(f"{base_url}/api/stocks/scores?top_n=5")
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            print(f"   Status: OK")
            scores = data.get('data', {}).get('items', [])
            print(f"   Scores count: {len(scores)}")
            if scores:
                print(f"   Top stock: {scores[0].get('code')} - Score: {scores[0].get('total_score')}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 50)
    print("API Tests Complete!")

if __name__ == "__main__":
    test_api()
