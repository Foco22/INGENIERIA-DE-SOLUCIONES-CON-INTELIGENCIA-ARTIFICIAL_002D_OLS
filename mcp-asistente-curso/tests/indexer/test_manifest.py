"""Tests del diff-aware processing (indexer/manifest.py). Ver plan.md §4.1, paso 2.

No usa PDFs reales ni OCR — son archivos de texto sintéticos, para que corra
en segundos y no dependa de indexer/ingest.py.
"""

from __future__ import annotations

from pathlib import Path

from indexer.manifest import changed_sources, hash_file, load_manifest, save_manifest
from utils.paths import PdfSource


def _fake_source(path: Path, tipo: str = "clase") -> PdfSource:
    return PdfSource(path=path, tipo=tipo, experiencia="Experiencia de Aprendizaje 1", clase="Clase 1.1")


def test_hash_file_cambia_con_el_contenido(tmp_path: Path) -> None:
    f = tmp_path / "a.pdf"
    f.write_bytes(b"contenido original")
    h1 = hash_file(f)

    f.write_bytes(b"contenido modificado")
    h2 = hash_file(f)

    assert h1 != h2


def test_load_manifest_vacio_si_no_existe(tmp_path: Path) -> None:
    assert load_manifest(tmp_path / "no_existe.json") == {}


def test_save_y_load_manifest_roundtrip(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    save_manifest({"clase/a.pdf": "hash1"}, manifest_path)

    assert load_manifest(manifest_path) == {"clase/a.pdf": "hash1"}


def test_changed_sources_primera_corrida_reprocesa_todo(tmp_path: Path) -> None:
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"contenido")
    sources = [_fake_source(pdf)]

    to_process, manifest = changed_sources(sources, previous_manifest={}, root=tmp_path)

    assert to_process == sources
    assert set(manifest) == {"a.pdf"}


def test_changed_sources_salta_lo_que_no_cambio(tmp_path: Path) -> None:
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"contenido")
    source = _fake_source(pdf)

    # Simula una corrida anterior donde este PDF ya quedó procesado.
    _, previous_manifest = changed_sources([source], previous_manifest={}, root=tmp_path)

    to_process, _ = changed_sources([source], previous_manifest, root=tmp_path)

    assert to_process == []


def test_changed_sources_reprocesa_solo_lo_modificado(tmp_path: Path) -> None:
    pdf_a = tmp_path / "a.pdf"
    pdf_a.write_bytes(b"contenido a")
    pdf_b = tmp_path / "b.pdf"
    pdf_b.write_bytes(b"contenido b")
    source_a, source_b = _fake_source(pdf_a), _fake_source(pdf_b)

    _, previous_manifest = changed_sources(
        [source_a, source_b], previous_manifest={}, root=tmp_path
    )

    pdf_a.write_bytes(b"contenido a, modificado")  # solo A cambia
    to_process, _ = changed_sources([source_a, source_b], previous_manifest, root=tmp_path)

    assert to_process == [source_a]
