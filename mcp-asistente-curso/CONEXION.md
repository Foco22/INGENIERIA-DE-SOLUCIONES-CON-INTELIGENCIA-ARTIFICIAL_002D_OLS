# Conectar el asistente del curso a tu Claude

Servidor MCP real, corriendo en producción:

```
https://mcp-asistente-curso-99135830306.northamerica-northeast1.run.app/mcp
```

Necesitás el bearer token del curso (pedíselo a quien administra el servidor — no va en este archivo, no se comitea con el token real).

## Opción A — Claude Code (terminal)

```bash
claude mcp add --transport http asistente-curso https://mcp-asistente-curso-99135830306.northamerica-northeast1.run.app/mcp --header "Authorization: Bearer TU_TOKEN_ACA"
```

Después abrí una conversación nueva y preguntale algo del curso, ej. *"¿qué es RAG y cómo se relaciona con embeddings?"*

## Opción B — Claude Desktop (la app)

Editar `claude_desktop_config.json`:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "asistente-curso": {
      "url": "https://mcp-asistente-curso-99135830306.northamerica-northeast1.run.app/mcp",
      "headers": {
        "Authorization": "Bearer TU_TOKEN_ACA"
      }
    }
  }
}
```

Reemplazá `TU_TOKEN_ACA` por el token real, guardá, reiniciá Claude Desktop.

## Qué puede responder

- `buscar_contenido`: conceptos de materia, relaciones entre temas, contenido de una clase puntual.
- `detalle_pruebas`: pauta, indicadores de logro, requisitos de entrega, % de ponderación de las evaluaciones.

No da fechas de calendario absolutas (los PDFs del curso solo tienen semanas relativas del cronograma).
