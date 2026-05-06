from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CoinPackagePurchase(BaseModel):
    package_slug: str  # starter | bronze | silver | gold | platinum


class SeedInfo(BaseModel):
    server_seed_hash: str
    client_seed: str
    nonce: int


class SeedRotateOut(BaseModel):
    revealed_server_seed: str | None
    new_server_seed_hash: str
    new_client_seed: str


class BetIn(BaseModel):
    game: str
    bet_coins: int = Field(gt=0)
    bet_input: dict[str, Any] = Field(default_factory=dict)


class RoundOut(BaseModel):
    id: str
    game: str
    bet_coins: int
    payout_coins: int
    multiplier: float
    server_seed_hash: str
    server_seed: str | None
    client_seed: str
    nonce: int
    outcome: dict[str, Any]
    bet_input: dict[str, Any]
