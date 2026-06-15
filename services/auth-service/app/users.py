from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Hardcoded user store — no database needed for this service.
# In production you would load users from a database, but for this course
# the store is intentionally simple so the focus stays on the JWT mechanics.
#
# Three users exist:
#   testuser      — role: gamer   (represents a regular platform user)
#   admin         — role: admin   (can perform privileged operations, e.g. DELETE /games)
#   activity-service — role: service (used for M2M calls between services)
USERS: dict[str, dict] = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("password"),
        "role": "gamer",
    },
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("adminpass"),
        "role": "admin",
    },
    "activity-service": {
        "username": "activity-service",
        "hashed_password": pwd_context.hash("m2m-secret"),
        "role": "service",
    },
}


def authenticate_user(username: str, password: str) -> dict | None:
    """Return the user dict if credentials are valid, None otherwise."""
    user = USERS.get(username)
    if not user:
        return None
    if not pwd_context.verify(password, user["hashed_password"]):
        return None
    return user
