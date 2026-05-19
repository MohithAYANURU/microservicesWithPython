import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import Base, User

USERS = [
    {"username": "nova",        "email": "nova@gamehub.io",    "bio": "Explorer of virtual worlds."},
    {"username": "alex_g",      "email": "alex@gamehub.io",    "bio": "Speedrunner. Coffee addict."},
    {"username": "maya_r",      "email": "maya@gamehub.io",    "bio": "RPG lover, lore hunter."},
    {"username": "thunderbyte", "email": "thunder@gamehub.io", "bio": "FPS main, occasional cozy gamer."},
    {"username": "pixel_queen", "email": "pixel@gamehub.io",   "bio": "Completionist. 100% or nothing."},
]

FAKE_HASH = "hashed_password"

def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    imported = 0
    for data in USERS:
        existing = db.query(User).filter(User.username == data["username"]).first()
        if existing:
            continue
        user = User(
            username=data["username"],
            email=data["email"],
            hashed_password=FAKE_HASH,
            bio=data["bio"],
        )
        db.add(user)
        imported += 1

    db.commit()
    db.close()
    print(f"Imported {imported} users.")

if __name__ == "__main__":
    run()
