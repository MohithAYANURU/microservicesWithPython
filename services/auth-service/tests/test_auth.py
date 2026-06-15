from pathlib import Path
import sys

from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from app.main import app  # noqa: E402


def test_token_round_trip_returns_payload():
    client = TestClient(app)

    token_response = client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "password"},
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    me_response = client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    body = me_response.json()
    assert body["sub"] == "testuser"
    assert body["role"] == "gamer"
    assert body["exp"]
