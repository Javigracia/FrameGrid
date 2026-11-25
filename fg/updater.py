# FrameGrid — Copyright (C) 2026 Javier
# SPDX-License-Identifier: GPL-3.0-or-later
"""Actualización desde las Releases de GitHub.

Flujo: consultar la última release -> descargar FrameGrid-X.Y.Z.zip -> comprobar su
SHA-256 con el archivo FrameGrid-X.Y.Z.zip.sha256 de la misma release (si existe) ->
descomprimir en una carpeta temporal sin permitir rutas fuera de ella -> validar que
es FrameGrid y que la versión coincide -> copia de seguridad de la instalación actual
-> bash install.sh -> reiniciar FrameGrid desde la copia instalada.
Nunca se actualiza sin que el usuario lo pida.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO = "Javigracia/FrameGrid"
API = os.environ.get("FRAMEGRID_UPDATE_API", "https://api.github.com")
ASSET_RX = re.compile(r"^FrameGrid-(\d+\.\d+\.\d+)\.zip$")
MAX_ZIP = 50 * 1024 * 1024
CACHE_SECONDS = 6 * 3600
UA = "FrameGrid-updater"
INSTALL_DIR = Path.home() / ".local/share/framegrid"


class UpdateError(Exception):
    pass


def parse_version(v: str) -> tuple[int, ...]:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", v or "")
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def _get(url: str, timeout: float, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(MAX_ZIP + 1)


class Updater:
    def __init__(self, current: str, here: Path):
        self.current = current
        self.here = Path(here).resolve()
        self._cache = None
        self._cache_time = 0.0

    # ------------------------------------------------ comprobar
    def check(self, force: bool = False) -> dict:
        if not force and self._cache and time.time() - self._cache_time < CACHE_SECONDS:
            return self._cache
        info = {"current": self.current, "available": False, "latest": None, "error": None,
                "git": (self.here / ".git").exists()}
        try:
            rel = json.loads(_get(f"{API}/repos/{REPO}/releases/latest", timeout=6))
            zip_asset = sha_asset = None
            for a in rel.get("assets", []):
                m = ASSET_RX.match(a.get("name", ""))
                if m:
                    zip_asset = a
            if zip_asset:
                for a in rel.get("assets", []):
                    if a.get("name") == zip_asset["name"] + ".sha256":
                        sha_asset = a
            latest = (rel.get("tag_name") or "").lstrip("v")
            info.update({
                "latest": latest,
                "name": rel.get("name") or rel.get("tag_name"),
                "notes": rel.get("body") or "",
                "url": rel.get("html_url"),
                "published": rel.get("published_at"),
                "zip_url": zip_asset and zip_asset.get("browser_download_url"),
                "zip_size": zip_asset and zip_asset.get("size"),
                "sha_url": sha_asset and sha_asset.get("browser_download_url"),
                "available": bool(zip_asset) and parse_version(latest) > parse_version(self.current),
            })
        except urllib.error.HTTPError as e:
            info["error"] = f"GitHub respondió {e.code}"
        except Exception as e:
            info["error"] = f"Sin conexión con GitHub: {getattr(e, 'reason', e)}"
        self._cache, self._cache_time = info, time.time()
        return info

    # ------------------------------------------------ aplicar
    def apply(self) -> dict:
        if (self.here / ".git").exists():
            raise UpdateError("FrameGrid se ejecuta desde un repositorio git: actualiza con «git pull».")
        info = self.check(force=True)
        if info.get("error"):
            raise UpdateError(info["error"])
        if not info.get("available"):
            raise UpdateError("Ya tienes la última versión.")
        latest = info["latest"]

        data = _get(info["zip_url"], timeout=120, accept="application/octet-stream")
        if len(data) > MAX_ZIP:
            raise UpdateError("La descarga es demasiado grande.")
        digest = hashlib.sha256(data).hexdigest()
        verified = False
        if info.get("sha_url"):
            expected = _get(info["sha_url"], timeout=30, accept="application/octet-stream").decode(
                "utf-8", "replace").strip().split()[0].lower()
            if expected != digest:
                raise UpdateError("La suma de verificación SHA-256 no coincide: actualización cancelada.")
            verified = True

        tmp = Path(tempfile.mkdtemp(prefix="framegrid-update-"))
        try:
            zpath = tmp / "update.zip"
            zpath.write_bytes(data)
            out = tmp / "x"
            out.mkdir()
            self._safe_extract(zpath, out)
            src = out / "FrameGrid"
            fg_py = src / "framegrid.py"
            if not fg_py.is_file() or not (src / "install.sh").is_file():
                raise UpdateError("El zip descargado no tiene la estructura de FrameGrid.")
            m = re.search(r'^VERSION = "([^"]+)"', fg_py.read_text("utf-8", "replace"), re.M)
            if not m or parse_version(m.group(1)) != parse_version(latest):
                raise UpdateError("La versión del zip no coincide con la de la release.")

            backup = self._backup()
            r = subprocess.run(["bash", str(src / "install.sh")], cwd=src, capture_output=True,
                               text=True, timeout=120)
            if r.returncode != 0:
                raise UpdateError("install.sh falló: " + (r.stderr or r.stdout).strip()[-300:])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        self._cache = None
        return {"ok": True, "version": latest, "verified": verified, "sha256": digest,
                "backup": str(backup) if backup else None, "restart_from": str(INSTALL_DIR / "framegrid.py")}

    @staticmethod
    def _safe_extract(zpath: Path, out: Path):
        root = out.resolve()
        with zipfile.ZipFile(zpath) as z:
            for info in z.infolist():
                name = info.filename
                if name.startswith("__MACOSX/") or name.endswith(".DS_Store"):
                    continue
                dest = (out / name).resolve()
                if dest != root and root not in dest.parents:
                    raise UpdateError("El zip contiene rutas no permitidas: actualización cancelada.")
                if info.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                    continue
                if (info.external_attr >> 16) & 0o170000 == 0o120000:  # enlaces simbólicos: fuera
                    raise UpdateError("El zip contiene rutas no permitidas: actualización cancelada.")
                dest.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as fsrc, open(dest, "wb") as fdst:
                    shutil.copyfileobj(fsrc, fdst)

    def _backup(self) -> Path | None:
        """Copia de la instalación actual en ~/.local/share/framegrid-backups/<versión> (se guardan 3)."""
        if not INSTALL_DIR.is_dir():
            return None
        root = INSTALL_DIR.parent / "framegrid-backups"
        root.mkdir(parents=True, exist_ok=True)
        dest = root / f"{self.current}-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copytree(INSTALL_DIR, dest, ignore=shutil.ignore_patterns("__pycache__"))
        for old in sorted(root.iterdir())[:-3]:
            shutil.rmtree(old, ignore_errors=True)
        return dest
