"""Provably-fair RNG: HMAC-SHA256(server_seed, client_seed:nonce:cursor) -> bytes -> floats.

Compatible with public verifier:
    bytes(i*4..i*4+4) -> uint32 -> float = uint32 / 2**32  in [0, 1)
"""
from __future__ import annotations

import hashlib
import hmac


class Rng:
    """Deterministic RNG bound to (server_seed, client_seed, nonce). Cursor advances per draw."""

    __slots__ = ("_buffer", "_buffer_pos", "_cursor", "client_seed", "nonce", "server_seed")

    def __init__(self, server_seed: str, client_seed: str, nonce: int) -> None:
        self.server_seed = server_seed
        self.client_seed = client_seed
        self.nonce = int(nonce)
        self._buffer: bytes = b""
        self._buffer_pos: int = 0
        self._cursor: int = 0

    def _refill(self) -> None:
        msg = f"{self.client_seed}:{self.nonce}:{self._cursor}".encode()
        self._buffer = hmac.new(self.server_seed.encode(), msg, hashlib.sha256).digest()
        self._buffer_pos = 0
        self._cursor += 1

    def _next_uint32(self) -> int:
        if self._buffer_pos + 4 > len(self._buffer):
            self._refill()
        v = int.from_bytes(self._buffer[self._buffer_pos : self._buffer_pos + 4], "big")
        self._buffer_pos += 4
        return v

    def uniform(self) -> float:
        return self._next_uint32() / 2**32

    def randint(self, lo: int, hi: int) -> int:
        """Inclusive both ends."""
        if hi <= lo:
            return lo
        n = hi - lo + 1
        return lo + int(self.uniform() * n)


def commit(server_seed: str) -> str:
    return hashlib.sha256(server_seed.encode()).hexdigest()
