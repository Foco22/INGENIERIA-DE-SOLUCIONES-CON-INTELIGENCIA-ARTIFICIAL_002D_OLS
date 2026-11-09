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

---

## Tarea del estudiante

**Objetivo:** agregar **una tool nueva** a este servidor MCP y usarla desde tu
**Claude Code local**.

### 1. Agrega la tool

En `server.py`, junto a las otras tools, crea una función con el decorador
`@mcp.tool()`. El nombre, los tipos y el docstring son lo que Claude lee para decidir
cuándo usarla, así que descríbela bien. Ejemplo:

```python
@mcp.tool()
def get_evaluation_info() -> dict:
    """Información de las evaluaciones del curso: tipos, ponderaciones y fechas."""
    return {
        "evaluaciones": [
            {"nombre": "Evaluación 1", "ponderacion": "30%"},
            # completa con la información real de tu curso
        ]
    }
```

Elige una idea propia (no tiene que ser esta). Algunas opciones:

- Las evaluaciones del curso y sus fechas.
- Un resumen de una clase específica (`get_class_summary(numero: int)`).
- El glosario de términos de IA del curso (`define_term(term: str)`).
- Una tool que use `retrieve()` filtrando por tema.

Requisitos mínimos: nombre en inglés y en `snake_case`, tipos en los parámetros y un
docstring claro que explique qué hace y qué devuelve.

### 2. Córrelo en local

Con tu `.env` listo (ver «Cómo correrlo en local»):

```powershell
python server.py
```

Comprueba que levantó con `http://localhost:8080/health` (debe mostrar `ok`).

### 3. Conéctalo a tu Claude Code local

```powershell
claude mcp add --transport http curso-local http://localhost:8080/mcp --header "X-API-Key: <tu MCP_API_KEY del .env>"
```

Verifica la conexión:

```powershell
claude mcp list
```

`curso-local` debe aparecer como conectado. Dentro de Claude Code también puedes
escribir `/mcp`. Si agregaste la tool con el servidor ya corriendo, reinícialo
(`Ctrl+C` y `python server.py`) y reconecta.

### 4. Pruébala

Abre Claude Code y haz una pregunta que obligue a usar tu tool nueva, por ejemplo:
«¿cuáles son las evaluaciones del curso?». Claude pedirá permiso para ejecutar la
tool la primera vez.

### Entregable

- Tu `server.py` con la tool nueva.
- Una captura de Claude Code usando tu tool (se debe ver la llamada a la tool y la
  respuesta).
- Una explicación breve: ¿por qué escribiste el docstring de esa manera? ¿Qué pasa
  con la respuesta de Claude si lo dejas vacío o ambiguo?

### Bonus

Despliega tu versión en tu propio Cloud Run, o agrega una segunda tool que reciba un
parámetro y valide su entrada.
