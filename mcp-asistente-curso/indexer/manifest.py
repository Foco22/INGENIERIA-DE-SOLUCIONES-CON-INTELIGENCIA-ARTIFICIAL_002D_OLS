"""Hash sha256 por PDF para diff-aware processing: solo reprocesa lo nuevo/modificado.

Ver plan.md §4.1, paso 2. Específico de esta etapa, no se comparte con server/ ni eval/.

El manifest.json local (data/manifest.json, gitignored) es la copia de trabajo.
En CI, el runner de GitHub Actions no persiste estado entre corridas — es
responsabilidad de indexer/run.py (Fase 6) bajarlo de GCS antes de llamar acá
y subirlo de vuelta después. Este módulo solo tiene la lógica de diff en sí,
sin saber nada de GCS.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from utils.paths import REPO_ROOT, PdfSource

MANIFEST_PATH = REPO_ROOT / "mcp-asistente-curso" / "data" / "manifest.json"


def hash_file(path: Path) -> str:
    """sha256 del contenido del archivo."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, str]:
    """Carga el manifest previo: {archivo: hash}. Vacío si no existe (primera corrida)."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, str], path: Path = MANIFEST_PATH) -> None:
    """Guarda el manifest actualizado, ordenado para que el diff en git sea legible."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def changed_sources(
    sources: list[PdfSource],
    previous_manifest: dict[str, str],
    root: Path = REPO_ROOT,
) -> tuple[list[PdfSource], dict[str, str]]:
    """Compara el hash actual de cada PdfSource contra el manifest previo.

    Devuelve (fuentes_a_reprocesar, manifest_actual):
    - fuentes_a_reprocesar: nuevas o con hash distinto al de la última corrida.
    - manifest_actual: hash de TODAS las fuentes (clases + evaluaciones),
      listo para guardar con save_manifest() una vez reprocesadas.

    La clave de cada entrada es la ruta relativa a `root` (por defecto REPO_ROOT,
    igual que `PdfSource.archivo`) — estable entre corridas en distintas máquinas,
    a diferencia de una ruta absoluta. `root` es parametrizable para poder testear
    con archivos sintéticos fuera del repo.
    """
    current_manifest: dict[str, str] = {}
    to_reprocess: list[PdfSource] = []
    for source in sources:
        key = str(source.path.relative_to(root))
        current_hash = hash_file(source.path)
        current_manifest[key] = current_hash
        if previous_manifest.get(key) != current_hash:
            to_reprocess.append(source)
    return to_reprocess, current_manifest
