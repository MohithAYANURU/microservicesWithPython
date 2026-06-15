from jose import JWTError, jwt
import httpx
from fastapi import FastAPI, HTTPException, Request, Response

from app.config import settings

app = FastAPI(title="gateway", version="1.0.0")

ROUTES: dict[str, str] = {
    "users":      settings.user_service_url,
    "games":      settings.game_service_url,
    "activities": settings.activity_service_url,
    # Added in Module 4
    "notifications": settings.notification_service_url,
    # Added in Module 5
    "consent":       settings.logging_service_url,
    "logs":          settings.logging_service_url,
    # Added in Module 6
    "auth":          settings.auth_service_url,
}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request: Request, path: str):
    # Step 1 — parse the resource name from the path
    segments = path.split("/")
    if len(segments) < 2:
        return Response(status_code=404, content="Not found")

    resource = segments[1]
    is_public_auth_token = len(segments) >= 3 and resource == "auth" and segments[2] == "token"

    # Step 2 — look up the target service
    target_base = ROUTES.get(resource)
    if target_base is None:
        return Response(status_code=404, content=f"Unknown resource: {resource}")

    if not is_public_auth_token:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Step 3 — forward the request
    target_url = f"{target_base}/{path}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers.raw,
                content=await request.body(),
                params=request.query_params,
            )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        )
    # Step 4 — handle unreachable service
    except httpx.RequestError:
        return Response(status_code=503, content="Service unavailable")
