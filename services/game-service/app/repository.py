# Infrastructure layer — raw database queries.
#
# Implement these four functions. Each takes `db: Session` as its first argument.
# No business logic here — only ORM queries.
#
# - create_game(db, data) -> Game
# - get_game(db, game_id) -> Game | None
# - list_games(db, limit, offset) -> tuple[list[Game], int]
# - search_games(db, q, limit, offset) -> tuple[list[Game], int]
#   Hint: filter by title using .ilike(f"%{q}%") for case-insensitive search
from redis import RedisError
from sqlalchemy.orm import Session

from app.infrastructure.cache import delete_game_summary, set_game_summary
from app.models import Game
from app.schemas import GameCreate


def create_game(db: Session, data: GameCreate) -> Game:
    game = Game(
        title=data.title,
        genre=data.genre,
        platform=data.platform,
        release_year=data.release_year,
        cover_url=data.cover_url,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    try:
        set_game_summary(
            game.id,
            {
                "id": game.id,
                "title": game.title,
                "genre": game.genre,
                "platform": game.platform,
            },
        )
    except RedisError:
        pass
    return game


def get_game(db: Session, game_id: str) -> Game | None:
    return db.query(Game).filter(Game.id == game_id).first()


def delete_game(db: Session, game_id: str) -> bool:
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        return False

    db.delete(game)
    db.commit()
    try:
        delete_game_summary(game_id)
    except RedisError:
        pass
    return True


def list_games(db: Session, limit: int = 20, offset: int = 0) -> tuple[list[Game], int]:
    total = db.query(Game).count()
    games = db.query(Game).offset(offset).limit(limit).all()
    return games, total


def search_games(db: Session, q: str, limit: int = 20, offset: int = 0) -> tuple[list[Game], int]:
    query = db.query(Game).filter(Game.title.ilike(f"%{q}%"))
    total = query.count()
    games = query.offset(offset).limit(limit).all()
    return games, total
