from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GameSummary(BaseModel):
    """Embedded game data returned by game-service. Matches GET /v1/games/{id}."""
    id: str
    title: str
    genre: str
    platform: str
    cover_url: Optional[str] = None


class ActivityCreate(BaseModel):
    user_id: str
    game_id: str
    action: str  # played | completed | reviewed | wishlist_added
    duration_minutes: Optional[int] = None


class ActivityOut(BaseModel):
    id: str
    user_id: str
    action: str
    duration_minutes: Optional[int]
    created_at: datetime
    game: Optional[GameSummary] = None  # null when game-service is unreachable

    model_config = {"from_attributes": True}


class ActivityList(BaseModel):
    """Paginated envelope — all list endpoints return this shape."""
    items: list[ActivityOut]
    total: int
    limit: int
    offset: int
