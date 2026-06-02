from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
resp = client.post(
    '/predict',
    json={
        'symptoms': ['cough', 'fever'],
        'profile': {'gender': 'male', 'age': 30}
    }
)
print(resp.status_code)
print(sorted(resp.json().keys()))
print(resp.json())
