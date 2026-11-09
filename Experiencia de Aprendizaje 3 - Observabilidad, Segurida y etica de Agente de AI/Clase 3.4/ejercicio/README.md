# MCP del curso — Ingeniería de Soluciones con IA (DuocUC)

Servidor MCP (Streamable HTTP) que expone la información del curso para que
Claude (Desktop o Code) pueda consultarla. Se despliega en Google Cloud Run.

## Tools

| Tool | Qué hace |
|------|----------|
| `search_course_content(query, top_k)` | Búsqueda vectorial en los apuntes del curso (MongoDB Atlas + embeddings de OpenAI) |
| `get_course_info()` | Nombre, institución, profesor y temas |
| `list_course_topics()` | Lista de temas |

## Estructura

```
server.py                    servidor MCP + middleware de API key
agent_app/tools.py           retrieve(): búsqueda vectorial en Mongo
agent_app/utils/embeddings.py  cliente de embeddings (text-embedding-3-small)
Dockerfile, requirements.txt
```

## Variables de entorno

| Variable | Para qué |
|----------|----------|
| `OPENAI_API_KEY` | Embeddings de la consulta |
| `MONGODB_CONNECTION_STRING` | Base vectorial con los apuntes |
| `MCP_API_KEY` | Clave que deben enviar los clientes. **Sin ella el servidor no arranca.** |
| `PORT` | Puerto (por defecto `8080`; Cloud Run lo define solo) |

## Cómo correrlo en local

```powershell
cd "Clase 3.4/ejercicio"
pip install -r requirements.txt
```

Crea un `.env` (ya está en `.gitignore`) con:

```
OPENAI_API_KEY=...
MONGODB_CONNECTION_STRING=...
MCP_API_KEY=cualquier-clave-para-pruebas
```

```powershell
python server.py
```

Queda en `http://localhost:8080/mcp` (y `/health` para comprobar que vive).
Abrir `/mcp` en el navegador da un error de `text/event-stream`: es normal, solo
responde a clientes MCP.

Probar con el inspector:

```powershell
npx @modelcontextprotocol/inspector
```

Transporte **Streamable HTTP**, URL `http://localhost:8080/mcp`, y agrega la
cabecera `X-API-Key` con tu `MCP_API_KEY`.

Con Docker:

```powershell
docker build -t curso-mcp .
docker run -p 8080:8080 --env-file .env curso-mcp
```

## La clave de acceso (API key)

El endpoint es público en internet, así que se protege con una clave. El servidor
rechaza con `401` cualquier llamada a `/mcp` que no traiga la clave en alguna de
estas cabeceras:

- `X-API-Key: <clave>`
- `Authorization: Bearer <clave>`

`/health` queda abierto. La comparación se hace con `hmac.compare_digest`.

### Cómo se generó

Es un valor aleatorio de 32 bytes, generado con la librería `secrets` de Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Se guardó como secreto del repositorio de GitHub, sin escribirla en ningún archivo:

```powershell
gh secret set MCP_API_KEY --body "<la-clave>"
```

El workflow la inyecta como variable de entorno `MCP_API_KEY` del servicio en
Cloud Run. **Nunca la subas al repositorio.** Para rotarla: genera otra, vuelve a
ejecutar `gh secret set MCP_API_KEY`, relanza el workflow y actualiza los clientes.

## Despliegue

`.github/workflows/deploy-mcp.yml` despliega a Cloud Run en cada push a `main` que
toque esta carpeta, o a mano desde la pestaña Actions. Secretos del repo que usa:

`GCP_PROJECT_ID`, `GCP_SA_KEY`, `OPENAI_API_KEY`, `MONGODB_CONNECTION_STRING`, `MCP_API_KEY`

Al terminar imprime la URL del MCP (`https://<servicio>.run.app/mcp`).

## Conectar Claude

**Claude Desktop** — Settings → Connectors → Add custom connector:

- URL: `https://<servicio>.run.app/mcp`
- Encabezado: nombre `X-API-Key`, valor = tu clave

**Claude Code:**

```powershell
claude mcp add --transport http curso https://<servicio>.run.app/mcp --header "X-API-Key: <tu-clave>" --scope user
```

Luego pregunta, por ejemplo: «busca en mi curso qué es un guardrail».

## Notas de seguridad

- Cualquiera con la clave puede gastar tus créditos de OpenAI: no la compartas.
- Mongo Atlas debe permitir la IP de salida de Cloud Run (Network Access).
- Para algo más serio: guardar las claves en Secret Manager en vez de variables de
  entorno, y rotar `MCP_API_KEY` periódicamente.
