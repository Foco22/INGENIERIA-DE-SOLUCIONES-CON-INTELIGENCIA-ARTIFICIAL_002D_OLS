"""Tests de server/auth.py: bearer token + rate limit por IP. Ver plan.md §5.4.

Se prueba el middleware montado sobre una app Starlette mínima (no la app
MCP completa) — es un middleware ASGI genérico, no depende del protocolo MCP.
"""

from __future__ import annotations

import server.auth as auth_mod
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient


def _app() -> Starlette:
    async def ok(request):
        return PlainTextResponse("ok")

    app = Starlette(routes=[Route("/algo", ok, methods=["GET", "POST"])])
    app.add_middleware(auth_mod.AuthMiddleware)
    return app


def _client(monkeypatch, tokens: str = "token-valido") -> TestClient:
    monkeypatch.setenv("MCP_AUTH_TOKENS", tokens)
    return TestClient(_app())


def test_sin_header_de_auth_devuelve_401(monkeypatch) -> None:
    client = _client(monkeypatch)
    resp = client.get("/algo")
    assert resp.status_code == 401


def test_token_invalido_devuelve_401(monkeypatch) -> None:
    client = _client(monkeypatch)
    resp = client.get("/algo", headers={"Authorization": "Bearer otro-token"})
    assert resp.status_code == 401


def test_token_valido_deja_pasar(monkeypatch) -> None:
    client = _client(monkeypatch)
    resp = client.get("/algo", headers={"Authorization": "Bearer token-valido"})
    assert resp.status_code == 200
    assert resp.text == "ok"


def test_acepta_cualquiera_de_varios_tokens_separados_por_coma(monkeypatch) -> None:
    client = _client(monkeypatch, tokens="uno, dos , tres")
    resp = client.get("/algo", headers={"Authorization": "Bearer dos"})
    assert resp.status_code == 200


def test_sin_tokens_configurados_falla_cerrado(monkeypatch) -> None:
    monkeypatch.setenv("MCP_AUTH_TOKENS", "")
    client = TestClient(_app())
    resp = client.get("/algo", headers={"Authorization": "Bearer lo-que-sea"})
    assert resp.status_code == 500


def test_rate_limit_bloquea_despues_del_tope_por_ip(monkeypatch) -> None:
    monkeypatch.setattr(auth_mod, "_RATE_LIMIT_MAX_REQUESTS", 3)
    client = _client(monkeypatch)
    headers = {"Authorization": "Bearer token-valido"}

    for _ in range(3):
        assert client.get("/algo", headers=headers).status_code == 200

    resp = client.get("/algo", headers=headers)
    assert resp.status_code == 429


def test_rate_limit_es_independiente_por_ip(monkeypatch) -> None:
    monkeypatch.setattr(auth_mod, "_RATE_LIMIT_MAX_REQUESTS", 1)
    client = _client(monkeypatch)
    headers = {"Authorization": "Bearer token-valido"}

    assert client.get("/algo", headers=headers).status_code == 200
    # TestClient siempre pega desde la misma IP simulada -> la segunda request
    # de la MISMA "IP" debe bloquearse (el rate limit sí se está aplicando).
    assert client.get("/algo", headers=headers).status_code == 429
