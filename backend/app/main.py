from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
    yield
    await engine.dispose()


app = FastAPI(
    title="AccessiAI",
    description="AI-Powered Accessibility Audit Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
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
