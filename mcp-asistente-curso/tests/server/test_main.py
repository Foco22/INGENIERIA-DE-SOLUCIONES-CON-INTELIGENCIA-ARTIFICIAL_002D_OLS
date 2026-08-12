"""Tests de server/main.py: registro de tools + wiring del AuthMiddleware.

No repite la prueba de lógica de auth (eso está en tests/server/test_auth.py,
con apps Starlette frescas por test) -- acá solo confirma que la app real del
servidor tiene el middleware montado, y que buscar_contenido quedó
registrada. No se hacen requests reales contra `main_mod.app`: Starlette
cachea el middleware stack en el primer request, así que un test que
disparara una request fijaría el AuthMiddleware con el entorno de ESE
momento para el resto de la sesión de tests -- se inspecciona la
configuración de la app en su lugar, sin ese efecto secundario.
"""

from __future__ import annotations

import asyncio

import server.main as main_mod


def test_buscar_contenido_queda_registrada_como_tool() -> None:
    tools = asyncio.run(main_mod.mcp.list_tools())
    nombres = [t.name for t in tools]
    assert "buscar_contenido" in nombres


def test_auth_middleware_esta_montado_en_la_app_real() -> None:
    clases = [mw.cls for mw in main_mod.app.user_middleware]
    assert main_mod.AuthMiddleware in clases