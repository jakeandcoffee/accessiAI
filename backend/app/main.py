import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from strawberry.fastapi import GraphQLRouter

from app.api.routes import auth, dashboard, reports, scans, security, violations, websites
from app.core.config import settings
from app.core.security import get_current_user
from app.database.base import Base
from app.database.connection import engine, get_db
from app.graphql.queries import Query

import strawberry


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # create_all doesn't add columns to existing tables; backfill multi-page scan columns.
        for stmt in (
            "ALTER TABLE websites ADD COLUMN IF NOT EXISTS page_urls JSON NOT NULL DEFAULT '[]'",
            "ALTER TABLE scans ADD COLUMN IF NOT EXISTS page_results JSON",
            "ALTER TABLE scans ADD COLUMN IF NOT EXISTS scan_mode VARCHAR(20) NOT NULL DEFAULT 'entered'",
            "ALTER TABLE violations ADD COLUMN IF NOT EXISTS page_url VARCHAR(2048)",
            "ALTER TABLE websites ADD COLUMN IF NOT EXISTS attachments JSON NOT NULL DEFAULT '[]'",
        ):
            await conn.execute(text(stmt))
    yield
    await engine.dispose()


app = FastAPI(
    title="AccessiAI",
    description="AI-Powered Accessibility Audit Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(websites.router, prefix="/api")
app.include_router(scans.router, prefix="/api")
app.include_router(violations.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(security.router, prefix="/api")

schema = strawberry.Schema(query=Query)


async def get_graphql_context(request: Request):
    db = None
    user = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        from app.core.security import decode_access_token
        from app.database.connection import async_session
        from app.models.user import User
        from sqlalchemy import select
        from uuid import UUID

        token = auth_header.split(" ", 1)[1]
        user_id = decode_access_token(token)
        if user_id:
            db = async_session()
            result = await db.execute(select(User).where(User.id == UUID(user_id)))
            user = result.scalar_one_or_none()

    if db is None:
        from app.database.connection import async_session
        db = async_session()

    return {"db": db, "user": user, "request": request}


graphql_router = GraphQLRouter(schema, context_getter=get_graphql_context)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Serve built frontend (production mode for sharing via tunnel)
FRONTEND_DIST = Path("/app/frontend_dist")
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
