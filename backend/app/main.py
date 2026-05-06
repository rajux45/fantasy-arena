from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    admin as admin_api,
)
from app.api import (
    auth as auth_api,
)
from app.api import (
    casino as casino_api,
)
from app.api import (
    contests as contests_api,
)
from app.api import (
    kyc as kyc_api,
)
from app.api import (
    leaderboard as leaderboard_api,
)
from app.api import (
    matches as matches_api,
)
from app.api import (
    notifications as notifications_api,
)
from app.api import (
    promotions as promotions_api,
)
from app.api import (
    referrals as referrals_api,
)
from app.api import (
    responsible as responsible_api,
)
from app.api import (
    teams as teams_api,
)
from app.api import (
    tournaments as tournaments_api,
)
from app.api import wallet as wallet_api
from app.api import (
    webhooks as webhooks_api,
)
from app.api import (
    ws as ws_api,
)
from app.config import settings
from app.logging_config import setup_logging
from app.middleware.rate_limit import TokenBucketMiddleware


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="Fantasy Arena API",
        version="0.1.0",
        description=(
            "Production-grade fantasy sports + play-money social casino backend. "
            "See /docs for full schema."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TokenBucketMiddleware, capacity=120, refill_per_second=2.0)

    @app.get("/", tags=["meta"])
    def root() -> dict:
        return {"app": settings.app_name, "env": settings.env, "ok": True}

    @app.get("/healthz", tags=["meta"])
    def healthz() -> dict:
        return {"ok": True}

    @app.get("/readyz", tags=["meta"])
    def readyz() -> dict:
        return {"ok": True}

    app.include_router(auth_api.router)
    app.include_router(kyc_api.router)
    app.include_router(wallet_api.router)
    app.include_router(matches_api.router)
    app.include_router(teams_api.router)
    app.include_router(contests_api.router)
    app.include_router(casino_api.router)
    app.include_router(responsible_api.router)
    app.include_router(notifications_api.router)
    app.include_router(promotions_api.router)
    app.include_router(referrals_api.router)
    app.include_router(tournaments_api.router)
    app.include_router(leaderboard_api.router)
    app.include_router(admin_api.router)
    app.include_router(webhooks_api.router)
    app.include_router(ws_api.router)
    return app


app = create_app()
