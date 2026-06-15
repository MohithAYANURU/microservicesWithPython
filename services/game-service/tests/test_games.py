from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from app.database import Base, get_db  # noqa: E402
from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_create_game_returns_201_and_body(client: TestClient):
    response = client.post(
        "/v1/games/",
        json={
            "title": "Hollow Knight",
            "genre": "metroidvania",
            "platform": "PC",
            "release_year": 2017,
            "cover_url": "https://example.com/cover.jpg",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Hollow Knight"
    assert body["genre"] == "metroidvania"
    assert body["platform"] == "PC"
    assert body["release_year"] == 2017
    assert body["cover_url"] == "https://example.com/cover.jpg"
    assert body["id"]
    assert body["created_at"]


def test_get_game_by_id_returns_expected_game(client: TestClient):
    created = client.post(
        "/v1/games/",
        json={
            "title": "Celeste",
            "genre": "platformer",
            "platform": "Switch",
        },
    ).json()

    response = client.get(f"/v1/games/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["title"] == "Celeste"
    assert body["genre"] == "platformer"
    assert body["platform"] == "Switch"


def test_get_game_with_unknown_id_returns_404(client: TestClient):
    response = client.get("/v1/games/unknown-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_list_games_returns_paginated_envelope(client: TestClient):
    client.post(
        "/v1/games/",
        json={"title": "Hades", "genre": "roguelike", "platform": "PC"},
    )
    client.post(
        "/v1/games/",
        json={"title": "Stardew Valley", "genre": "simulation", "platform": "PC"},
    )

    response = client.get("/v1/games/?limit=20&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert len(body["items"]) == 2


def test_search_games_returns_only_matching_titles(client: TestClient):
    client.post(
        "/v1/games/",
        json={"title": "Portal", "genre": "puzzle", "platform": "PC"},
    )
    client.post(
        "/v1/games/",
        json={"title": "Portal 2", "genre": "puzzle", "platform": "PC"},
    )
    client.post(
        "/v1/games/",
        json={"title": "Dead Cells", "genre": "roguelike", "platform": "PC"},
    )

    response = client.get("/v1/games/search?q=portal")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["title"] for item in body["items"]} == {"Portal", "Portal 2"}


def test_health_returns_service_status(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "game-service"}


def test_delete_game_requires_admin_role(client: TestClient):
    created = client.post(
        "/v1/games/",
        json={"title": "Inside", "genre": "platformer", "platform": "PC"},
    ).json()

    gamer_token = jwt.encode(
        {"sub": "testuser", "role": "gamer"},
        settings.auth_secret_key,
        algorithm="HS256",
    )
    admin_token = jwt.encode(
        {"sub": "admin", "role": "admin"},
        settings.auth_secret_key,
        algorithm="HS256",
    )

    forbidden = client.delete(
        f"/v1/games/{created['id']}",
        headers={"Authorization": f"Bearer {gamer_token}"},
    )
    assert forbidden.status_code == 403
    assert forbidden.json() == {"detail": "Admin role required"}

    allowed = client.delete(
        f"/v1/games/{created['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert allowed.status_code == 200
    assert allowed.json() == {"detail": "Game deleted"}
