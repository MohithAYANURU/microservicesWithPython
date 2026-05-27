from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository import create_game, get_game, list_games, search_games
from app.schemas import GameCreate, GameList, GameOut


router = APIRouter(prefix="/v1/games", tags=["games"])


@router.post("", response_model=GameOut, status_code=201)
async def add_game(data: GameCreate, db: Session = Depends(get_db)):
    return create_game(db, data)


@router.get("", response_model=GameList)
async def fetch_all_games(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    items, total = list_games(db, limit=limit, offset=offset)
    return GameList(items=items, total=total, limit=limit, offset=offset)


@router.get("/search", response_model=GameList)
async def find_games(q: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    items, total = search_games(db, q=q, limit=limit, offset=offset)
    return GameList(items=items, total=total, limit=limit, offset=offset)


@router.get("/{game_id}", response_model=GameOut)
async def fetch_game(game_id: str, db: Session = Depends(get_db)):
    game = get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game
