"""Tests de utils/gcs.py: publish_index/download_latest_index. Ver plan.md §4.1 paso 6, §4.3.

`_bucket()` va simulado (monkeypatch) con un bucket/blob falsos en memoria —
no llama a GCP, así que corre en milisegundos y no depende de credenciales.
"""

from __future__ import annotations

from pathlib import Path

import utils.gcs as gcs_mod


class _FakeBlob:
    def __init__(self, store: dict[str, bytes], name: str) -> None:
        self._store = store
        self.name = name

    def upload_from_filename(self, path: str) -> None:
        self._store[self.name] = Path(path).read_bytes()

    def exists(self) -> bool:
        return self.name in self._store

    def download_to_filename(self, path: str) -> None:
        Path(path).write_bytes(self._store[self.name])


class _FakeBucket:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    def blob(self, name: str) -> _FakeBlob:
        return _FakeBlob(self.store, name)


def _con_bucket_falso(monkeypatch) -> _FakeBucket:
    bucket = _FakeBucket()
    monkeypatch.setattr(gcs_mod, "_bucket", lambda: bucket)
    return bucket


def test_publish_sube_a_latest_y_a_la_version_del_run_id(tmp_path: Path, monkeypatch) -> None:
    bucket = _con_bucket_falso(monkeypatch)
    (tmp_path / "chunks.parquet").write_bytes(b"contenido-chunks")
    (tmp_path / "graph.json").write_text('{"nodes": []}')
    # manifest.json no existe -> se salta, no debe romper la publicación.

    gcs_mod.publish_index(tmp_path, run_id="abc123")

    assert bucket.store["index/latest/chunks.parquet"] == b"contenido-chunks"
    assert bucket.store["index/abc123/chunks.parquet"] == b"contenido-chunks"
    assert "index/latest/graph.json" in bucket.store
    assert "index/latest/manifest.json" not in bucket.store


def test_download_trae_latest_a_local_dir(tmp_path: Path, monkeypatch) -> None:
    bucket = _con_bucket_falso(monkeypatch)
    bucket.store["index/latest/chunks.parquet"] = b"desde-gcs"

    destino = tmp_path / "data"
    gcs_mod.download_latest_index(destino)

    assert (destino / "chunks.parquet").read_bytes() == b"desde-gcs"
    assert not (destino / "graph.json").exists()  # no estaba en el bucket -> se salta


def test_download_crea_el_directorio_si_no_existe(tmp_path: Path, monkeypatch) -> None:
    _con_bucket_falso(monkeypatch)
    destino = tmp_path / "no-existe-todavia" / "data"

    gcs_mod.download_latest_index(destino)

    assert destino.is_dir()


def test_download_indice_vacio_no_falla(tmp_path: Path, monkeypatch) -> None:
    _con_bucket_falso(monkeypatch)  # bucket vacío, primera corrida antes de cualquier publish

    gcs_mod.download_latest_index(tmp_path)

    assert list(tmp_path.iterdir()) == []
