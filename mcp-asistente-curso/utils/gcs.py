"""Subir/bajar archivos del bucket de índice en Google Cloud Storage.

Usado por indexer/run.py para publicar el índice (plan.md §4.1, paso 6)
y por server/main.py para descargarlo al arrancar el contenedor (plan.md §4.3).

Layout del bucket (`GCS_BUCKET`): `index/latest/{manifest,chunks,graph}` +
una copia versionada en `index/<run_id>/` (mismo contenido) para poder hacer
rollback manual apuntando `latest/` a una versión anterior si hiciera falta.

Ambas funciones son no-op-friendly: si `GCS_BUCKET` no está seteado, el
caller decide no llamarlas (indexer/run.py y server/main.py solo publican/
descargan si la env var está presente) — así el flujo local de siempre
(leer/escribir directo en `data/`) sigue funcionando sin credenciales de GCP.
"""

from __future__ import annotations

import os
from pathlib import Path

from google.cloud import storage

_BUCKET_ENV = "GCS_BUCKET"
_ARCHIVOS = ("manifest.json", "chunks.parquet", "graph.json")


def _bucket() -> storage.Bucket:
    # project explícito (no confiar en el quota project que traigan las
    # credenciales activas) — evita el típico "User project specified in
    # the request is invalid" cuando las credenciales ADC locales quedaron
    # apuntando a otro proyecto por defecto.
    client = storage.Client(project=os.environ.get("GCP_PROJECT_ID"))
    return client.bucket(os.environ[_BUCKET_ENV])


def publish_index(local_dir: Path, run_id: str) -> None:
    """Sube los archivos de `local_dir` a `index/latest/` y a `index/<run_id>/`.

    Los que no existan en `local_dir` (ej. todavía no hay graph.json) se
    saltan en vez de fallar — publicar un índice parcial es mejor que no
    publicar nada.
    """
    bucket = _bucket()
    for nombre in _ARCHIVOS:
        origen = local_dir / nombre
        if not origen.exists():
            continue
        for destino in (f"index/latest/{nombre}", f"index/{run_id}/{nombre}"):
            bucket.blob(destino).upload_from_filename(str(origen))


def download_latest_index(local_dir: Path) -> None:
    """Descarga `index/latest/` a `local_dir` (la crea si no existe).

    Los blobs que no existan (índice todavía incompleto) se saltan en vez de
    fallar — igual que publish_index, un índice parcial es mejor que nada.
    """
    bucket = _bucket()
    local_dir.mkdir(parents=True, exist_ok=True)
    for nombre in _ARCHIVOS:
        blob = bucket.blob(f"index/latest/{nombre}")
        if blob.exists():
            blob.download_to_filename(str(local_dir / nombre))
