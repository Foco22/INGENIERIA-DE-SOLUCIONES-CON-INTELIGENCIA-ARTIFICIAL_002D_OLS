"""Middleware de autenticación: valida `Authorization: Bearer <token>` contra
el token compartido del curso (env var / secret). Rate limit básico por IP.

Ver plan.md §5.4 — decisión ya tomada: un único token compartido por todos
los estudiantes (no uno por persona), así que el rate limit no puede ser por
identidad y se aplica por IP en su lugar, solo para evitar que un abuso
puntual tumbe el servicio o dispare costos (no es un límite fino por usuario).

Middleware ASGI estándar de Starlette (no de la capa MCP) — se monta sobre
la app que devuelve `MCPServer.streamable_http_app()` en server/main.py, así
que corre para cualquier request HTTP antes de llegar al protocolo MCP.
"""

from __future__ import annotations

import os
import time
from collections import defaultdict

from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

load_dotenv()

_RATE_LIMIT_VENTANA_S = 60
_RATE_LIMIT_MAX_REQUESTS = 30  # por IP, dentro de la ventana


def _tokens_validos() -> set[str]:
    """MCP_AUTH_TOKENS: uno o más tokens separados por coma (permite rotar sin downtime)."""
    crudo = os.environ.get("MCP_AUTH_TOKENS", "")
    return {t.strip() for t in crudo.split(",") if t.strip()}


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._tokens = _tokens_validos()
        # IP -> timestamps de sus requests recientes. En memoria: no persiste
        # entre reinicios ni se comparte entre instancias si Cloud Run escala
        # a más de un contenedor — suficiente para "rate limit básico" (§5.4),
        # no un límite exacto entre instancias.
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if not self._tokens:
            # Sin tokens configurados en el entorno: falla cerrado, no abierto.
            return JSONResponse({"error": "servidor mal configurado (sin MCP_AUTH_TOKENS)"}, status_code=500)

        auth_header = request.headers.get("authorization", "")
        token = auth_header[len("Bearer ") :].strip() if auth_header.lower().startswith("bearer ") else None
        if token not in self._tokens:
            return JSONResponse({"error": "unauthorized"}, status_code=401)

        ip = request.client.host if request.client else "desconocida"
        ahora = time.time()
        recientes = [t for t in self._requests[ip] if ahora - t < _RATE_LIMIT_VENTANA_S]
        if len(recientes) >= _RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse({"error": "rate_limited"}, status_code=429)
        recientes.append(ahora)
        self._requests[ip] = recientes

        return await call_next(request)