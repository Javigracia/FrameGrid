#!/usr/bin/env python3
# FrameGrid — Copyright (C) 2026 Javier
# SPDX-License-Identifier: GPL-3.0-or-later
"""FrameGrid — gestor de carátulas (SteamGridDB) y colecciones para Steam Frame / SteamOS.

Arranca un servidor local en 127.0.0.1 y abre la interfaz en el navegador
(o en el navegador interno de Steam). Solo usa la librería estándar de Python.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import shutil
import socket
import subprocess
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fg import sgdb, steam  # noqa: E402
from fg.collections import Collections  # noqa: E402
from fg.live import SteamLive  # noqa: E402
from fg import imgutil  # noqa: E402
import base64  # noqa: E402
from fg.i18n import tr  # noqa: E402
from fg.pairing import Pairing  # noqa: E402

VERSION = "0.4.0"
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "framegrid"
CONFIG_FILE = CONFIG_DIR / "config.json"


# ---------------------------------------------------------------- config
def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text("utf-8"))
    except Exception:
        return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), "utf-8")
    os.chmod(CONFIG_FILE, 0o600)


class _nullcontext:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class App:
    def __init__(self, steam_root_override=None):
        self.cfg = load_config()
        if steam_root_override:
            self.cfg["steam_root"] = steam_root_override
        self.lock = threading.Lock()
        self.pairing = Pairing(self.set_api_key, tr)

    @property
    def root(self):
        return steam.find_steam_root(self.cfg.get("steam_root"))

    @property
    def live(self) -> SteamLive:
        return SteamLive(int(self.cfg.get("cef_port") or 8080))

    def user(self) -> steam.SteamUser:
        root = self.root
        if not root:
            raise RuntimeError("No encuentro la instalación de Steam (carpeta userdata).")
        users = steam.list_users(root)
        uid = self.cfg.get("user")
        if not uid or not any(u["id"] == uid for u in users):
            if not users:
                raise RuntimeError("No hay usuarios en Steam/userdata. Inicia sesión en Steam una vez.")
            uid = users[0]["id"]
        return steam.SteamUser(root, uid)

    def set_api_key(self, key: str, locked: bool = False) -> str | None:
        """Comprueba la clave contra SteamGridDB y la guarda. Devuelve un aviso si no se pudo verificar."""
        key = (key or "").strip()
        if not key:
            raise RuntimeError("API key de SteamGridDB no válida (401).")
        warn = None
        try:
            sgdb.SGDB(key, timeout=10).search("Portal")
        except sgdb.SGDBError as e:
            if "401" in str(e):
                raise
            warn = "No se pudo comprobar la clave ahora mismo; se ha guardado igualmente."
        with (_nullcontext() if locked else self.lock):
            self.cfg["api_key"] = key
            save_config({k: v for k, v in self.cfg.items() if v})
        return warn

    def sgdb(self) -> sgdb.SGDB:
        key = self.cfg.get("api_key")
        if not key:
            raise RuntimeError("Falta la API key de SteamGridDB (Ajustes).")
        return sgdb.SGDB(key)

    # ------------------------------------------------ modo de trabajo
    def mode(self) -> str:
        """live = Steam abierto con depurador CEF (como Decky) · files = Steam cerrado · limited = abierto sin depurador."""
        if self.live.available():
            return "live"
        return "limited" if steam.steam_running() else "files"

    def need_write_mode(self) -> str:
        m = self.mode()
        if m == "limited":
            raise RuntimeError("Steam está abierto y su depurador CEF no está activo. Pulsa «Activar modo en vivo» "
                               "y reinicia la Steam Frame (o activa Ajustes › Desarrollador › Depuración remota CEF).")
        return m

    def cef_flag_paths(self) -> list[Path]:
        paths = []
        for p in (self.root, Path.home() / ".steam/steam"):
            if p and p.exists():
                f = p.resolve() / ".cef-enable-remote-debugging"
                if f not in paths:
                    paths.append(f)
        return paths

    def enable_cef(self) -> list[str]:
        out = []
        for f in self.cef_flag_paths():
            f.touch(exist_ok=True)
            out.append(str(f))
        return out

    # ------------------------------------------------ acciones
    def state(self):
        root = self.root
        users = steam.list_users(root) if root else []
        cur = None
        try:
            cur = self.user().uid
        except Exception:
            pass
        return {
            "version": VERSION,
            "steam_root": str(root) if root else None,
            "users": users,
            "user": cur,
            "steam_running": steam.steam_running(),
            "mode": self.mode(),
            "cef_flag": any(f.exists() for f in self.cef_flag_paths()),
            "has_key": bool(self.cfg.get("api_key")),
            "lang": self.cfg.get("lang"),
        }

    def library(self):
        u = self.user()
        try:
            vdf_sc = {s["appid"]: s for s in u.shortcuts()}
        except Exception:
            vdf_sc = {}
        shortcuts = list(vdf_sc.values())
        if self.mode() == "live":
            try:
                live_sc = self.live.shortcuts()
                shortcuts = [{**vdf_sc.get(s["appid"], {}), **s} for s in live_sc]
            except Exception:
                pass
        items = shortcuts + u.steam_games()
        for it in items:
            it["art"] = u.art_status(it["appid"])
        return items

    def _apply_data(self, u: steam.SteamUser, appid: int, slot: str, data: bytes, ext: str, kind: str, mode: str):
        if ext == "webp":
            raise RuntimeError("Steam no carga WebP desde la carpeta grid; elige una imagen PNG/JPG.")
        if slot == "icon":
            if kind == "steam":
                if mode != "live":
                    raise RuntimeError("Cambiar el icono de un juego de Steam necesita el modo en vivo.")
                h = self.live.icon_hash(appid)
                if not h:
                    raise RuntimeError("Steam no da el icon_hash de este juego.")
                return {"path": str(u.poison_steam_icon(appid, h, data)), "note": None}
            path = u.write_art(appid, "icon", data, ext)
            if mode == "live":
                self.live.set_shortcut_icon(appid, str(path))
                return {"path": str(path), "note": None}
            if mode == "files":
                u.sync_shortcut_icons()
                return {"path": str(path), "note": None}
            return {"path": str(path), "note": "Icono guardado. Se vinculará al acceso directo cuando actives el modo en vivo."}
        if mode == "live":
            logo_pos = slot == "logo" and kind == "shortcut" and not (u.grid / f"{appid}.json").exists()
            self.live.set_artwork(appid, slot, data, ext, logo_pos)
            return {"path": None, "note": None}
        path = u.write_art(appid, slot, data, ext)
        note = "Guardada en la carpeta grid: se verá cuando reinicies la Steam Frame." if mode == "limited" else None
        return {"path": str(path), "note": note}

    def apply(self, appid: int, slot: str, url: str, kind: str):
        data, ext = sgdb.download(url)
        return self._apply_data(self.user(), appid, slot, data, ext, kind, self.mode())

    def apply_bytes(self, appid: int, slot: str, data: bytes, kind: str):
        ext = imgutil.kind(data)
        if ext is None:
            raise RuntimeError("El archivo no es una imagen PNG o JPG.")
        if ext in ("webp", "gif"):
            raise RuntimeError(f"Steam no carga imágenes {ext.upper()}. Conviértela a PNG o JPG.")
        if len(data) > 40 * 1024 * 1024:
            raise RuntimeError("La imagen es demasiado grande (máx. 40 MB).")
        return self._apply_data(self.user(), appid, slot, data, ext, kind, self.mode())

    def apply_local(self, appid: int, slot: str, path: str, kind: str):
        p = imgutil.safe_path(path)
        return self.apply_bytes(appid, slot, p.read_bytes(), kind)

    def remove(self, appid: int, slot: str, kind: str):
        u = self.user()
        mode = self.mode()
        if mode == "live":
            if slot == "icon":
                if kind == "steam":
                    raise RuntimeError("Para restaurar el icono original de un juego de Steam, verifica sus archivos.")
                u.remove_art(appid, "icon")
                self.live.set_shortcut_icon(appid, "")
            else:
                self.live.clear_artwork(appid, slot)
            return True
        return u.remove_art(appid, slot)

    def autofill(self, appids: list[int], slots: list[str], overwrite: bool):
        """Para cada entrada: busca por nombre, coge el primer juego y la mejor imagen de cada tipo."""
        u = self.user()
        api = self.sgdb()
        mode = self.mode()
        lib = {it["appid"]: it for it in self.library()}
        report = []
        for aid in appids:
            it = lib.get(aid)
            if not it:
                continue
            row = {"appid": aid, "name": it["name"], "applied": [], "error": None}
            try:
                game = None
                if it["type"] == "steam":
                    game = api.game_by_steam_appid(aid)
                if not game:
                    res = api.search(it["name"])
                    game = res[0] if res else None
                if not game:
                    row["error"] = "Sin resultados en SteamGridDB"
                else:
                    row["game"] = game.get("name")
                    for slot in slots:
                        if slot == "icon" and it["type"] == "steam":
                            continue
                        if not overwrite and u.art_path(aid, slot):
                            continue
                        for a in api.assets(slot, game["id"])[:3]:
                            data, ext = sgdb.download(a["url"])
                            if ext != "webp":
                                self._apply_data(u, aid, slot, data, ext, it["type"], mode)
                                row["applied"].append(slot)
                                break
            except Exception as e:  # seguimos con el resto
                row["error"] = str(e)
            report.append(row)
        return report

    # ------------------------------------------------ accesos directos
    def add_shortcut(self, name, exe, start_dir="", launch_options=""):
        if self.need_write_mode() == "live":
            return self.live.add_shortcut(name, exe, start_dir, launch_options)
        return self.user().add_shortcut(name, exe, start_dir, launch_options)

    def remove_shortcut(self, appid):
        if self.need_write_mode() == "live":
            self.live.remove_shortcut(appid)
            return True
        return self.user().remove_shortcut(appid)

    # ------------------------------------------------ colecciones
    def collections(self):
        m = self.mode()
        if m == "live":
            return {"mode": m, "items": self.live.collections()}
        return {"mode": m, "items": Collections(self.user().config).list()}

    def col_op(self, op, b):
        if self.need_write_mode() == "live":
            lv = self.live
            if op == "create":
                return {"id": lv.create_collection(b["name"], b.get("appids", []))}
            if op == "rename":
                lv.rename_collection(b["id"], b["name"])
            elif op == "delete":
                if b["id"] in ("favorite", "hidden"):
                    raise RuntimeError("No se pueden borrar Favoritos/Ocultos.")
                lv.delete_collection(b["id"])
            elif op == "member":
                lv.set_member(b["id"], [int(a) for a in b["appids"]], bool(b["member"]))
            return {"ok": True}
        col = Collections(self.user().config)
        if op == "create":
            cid = col.create(b["name"])
            if b.get("appids"):
                col.set_member(cid, b["appids"], True)
            return {"id": cid}
        if op == "rename":
            col.rename(b["id"], b["name"])
        elif op == "delete":
            col.delete(b["id"])
        elif op == "member":
            col.set_member(b["id"], b["appids"], bool(b["member"]))
        return {"ok": True}


# ---------------------------------------------------------------- HTTP
def make_handler(app: App, stop_event: threading.Event):
    web = HERE / "web"

    class H(BaseHTTPRequestHandler):
        server_version = "FrameGrid/" + VERSION

        def log_message(self, fmt, *a):
            if os.environ.get("FRAMEGRID_DEBUG"):
                super().log_message(fmt, *a)

        def _lang(self):
            h = (self.headers.get("X-Lang") or app.cfg.get("lang") or "es").lower()
            return "en" if h.startswith("en") else "es"

        def _err(self, e):
            return self._json({"error": tr(str(e), self._lang())}, 400)

        def _json(self, obj, code=200):
            lang = self._lang()
            if lang == "en":
                if isinstance(obj, dict):
                    for k in ("note", "warning"):
                        if obj.get(k):
                            obj[k] = tr(obj[k], lang)
                elif isinstance(obj, list):
                    for r in obj:
                        if isinstance(r, dict) and r.get("error"):
                            r["error"] = tr(r["error"], lang)
            b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b)

        def _file(self, p: Path):
            if not p or not p.is_file():
                self.send_error(404)
                return
            b = p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(p.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b)

        def _body(self):
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}") if n else {}

        def _guard(self):
            # Evita que una web cualquiera hable con este servidor local
            host = (self.headers.get("Host") or "").split(":")[0]
            if host not in ("127.0.0.1", "localhost"):
                self.send_error(403)
                return False
            origin = self.headers.get("Origin")
            if self.command == "POST" and origin and urllib.parse.urlparse(origin).hostname not in ("127.0.0.1", "localhost"):
                self.send_error(403)
                return False
            return True

        def do_GET(self):
            if not self._guard():
                return
            u = urllib.parse.urlparse(self.path)
            q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
            p = u.path
            try:
                if p in ("/", "/index.html"):
                    return self._file(web / "index.html")
                if p.startswith("/static/"):
                    f = (web / p[len("/static/"):]).resolve()
                    if web.resolve() not in f.parents:
                        return self.send_error(403)
                    return self._file(f)
                if p == "/api/state":
                    return self._json(app.state())
                if p == "/api/library":
                    return self._json(app.library())
                if p.startswith("/api/art/"):
                    _, _, _, aid, slot = p.split("/")
                    if slot not in steam.SLOTS:
                        return self.send_error(404)
                    return self._file(app.user().art_path(int(aid), slot))
                if p == "/api/sgdb/search":
                    return self._json(app.sgdb().search(q.get("q", "")))
                if p == "/api/sgdb/steam":
                    return self._json(app.sgdb().game_by_steam_appid(int(q["appid"])))
                if p == "/api/sgdb/assets":
                    return self._json(app.sgdb().assets(
                        q["slot"], int(q["game"]), int(q.get("page", 0)),
                        q.get("animated") == "1", q.get("nsfw") == "1", q.get("humor") == "1"))
                if p == "/api/local/list":
                    return self._json(imgutil.list_dir(q.get("dir") or app.cfg.get("images_dir")))
                if p == "/api/local/file":
                    f = imgutil.safe_path(q["path"])
                    if f.suffix.lower() not in imgutil.IMAGE_EXTS:
                        return self.send_error(403)
                    return self._file(f)
                if p == "/api/collections":
                    return self._json(app.collections())
                if p == "/api/pair/status":
                    st = app.pairing.status()
                    st["has_key"] = bool(app.cfg.get("api_key"))
                    return self._json(st)
                if p == "/api/pair/qr.svg":
                    svg = app.pairing.qr()
                    if not svg:
                        return self.send_error(404)
                    b = svg.encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "image/svg+xml")
                    self.send_header("Content-Length", str(len(b)))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    return self.wfile.write(b)
                return self.send_error(404)
            except Exception as e:
                return self._err(e)

        def do_POST(self):
            if not self._guard():
                return
            p = urllib.parse.urlparse(self.path).path
            try:
                b = self._body()
                with app.lock:
                    if p == "/api/config":
                        warn = None
                        if b.get("api_key"):
                            warn = app.set_api_key(b["api_key"], locked=True)
                        for k in ("user", "steam_root", "cef_port", "images_dir", "lang"):
                            if k in b:
                                app.cfg[k] = b[k] or None
                        save_config({k: v for k, v in app.cfg.items() if v})
                        st = app.state()
                        st["warning"] = warn
                        return self._json(st)
                    if p == "/api/pair/start":
                        return self._json(app.pairing.start(self._lang()))
                    if p == "/api/pair/stop":
                        app.pairing.stop()
                        return self._json({"ok": True})
                    if p == "/api/apply":
                        return self._json(app.apply(int(b["appid"]), b["slot"], b["url"], b.get("kind", "")))
                    if p == "/api/apply_local":
                        return self._json(app.apply_local(int(b["appid"]), b["slot"], b["path"], b.get("kind", "")))
                    if p == "/api/upload":
                        return self._json(app.apply_bytes(int(b["appid"]), b["slot"],
                                                          base64.b64decode(b["data"]), b.get("kind", "")))
                    if p == "/api/remove":
                        return self._json({"ok": app.remove(int(b["appid"]), b["slot"], b.get("kind", ""))})
                    if p == "/api/autofill":
                        return self._json(app.autofill([int(a) for a in b["appids"]],
                                                       b.get("slots", list(steam.SLOTS)),
                                                       bool(b.get("overwrite"))))
                    if p == "/api/shortcut/add":
                        return self._json({"appid": app.add_shortcut(b["name"], b["exe"], b.get("start_dir", ""),
                                                                     b.get("launch_options", ""))})
                    if p == "/api/shortcut/remove":
                        return self._json({"ok": app.remove_shortcut(int(b["appid"]))})
                    if p.startswith("/api/collections/"):
                        return self._json(app.col_op(p.rsplit("/", 1)[1], b))
                    if p == "/api/cef/enable":
                        return self._json({"files": app.enable_cef()})
                    if p == "/api/steam/start":
                        return self._json({"ok": steam.start_steam()})
                    if p == "/api/quit":
                        app.pairing.stop()
                        self._json({"ok": True})
                        stop_event.set()
                        return
                return self.send_error(404)
            except Exception as e:
                return self._err(e)

    return H


def free_port(start):
    for port in range(start, start + 50):
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No hay puertos libres")


def open_ui(url: str, mode: str):
    """mode: auto | xdg | steam | none"""
    if mode == "none":
        return
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    # En modo juego (gamescope) xdg-open no tiene navegador al que ir: usamos el de Steam
    in_gamescope = os.environ.get("XDG_CURRENT_DESKTOP", "").lower() == "gamescope" or bool(os.environ.get("GAMESCOPE_WAYLAND_DISPLAY"))
    if mode == "xdg" or (mode == "auto" and has_display and not in_gamescope and shutil.which("xdg-open")):
        try:
            r = subprocess.run(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            if r.returncode == 0:
                return
        except (OSError, subprocess.TimeoutExpired):
            pass
    if shutil.which("steam"):
        subprocess.Popen(["steam", f"steam://openurl/{url}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser(description="FrameGrid — carátulas SteamGridDB y colecciones para Steam Frame")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--open", choices=["auto", "xdg", "steam", "none"], default="auto",
                    help="cómo abrir la interfaz (steam = navegador interno de Steam)")
    ap.add_argument("--steam-root", help="ruta a la carpeta de Steam si no se detecta sola")
    ap.add_argument("--add-to-steam", action="store_true",
                    help="añade FrameGrid a la biblioteca de Steam (en vivo si el depurador CEF está activo)")
    ap.add_argument("--enable-cef", action="store_true",
                    help="crea .cef-enable-remote-debugging; luego hay que reiniciar la Steam Frame")
    ap.add_argument("--status", action="store_true", help="muestra el modo de trabajo y sale")
    ap.add_argument("--version", action="version", version=VERSION)
    args = ap.parse_args()

    app = App(args.steam_root)
    if args.status:
        st = app.state()
        print(f"Steam: {st['steam_root']}  usuario: {st['user']}  abierto: {st['steam_running']}")
        print(f"Modo: {st['mode']}  (archivo CEF presente: {st['cef_flag']})")
        if st["mode"] == "live":
            print("Contexto de Steam:", app.live.check())
        return
    if args.enable_cef:
        for f in app.enable_cef():
            print("Creado", f)
        print("Reinicia la Steam Frame (o Steam) para que el depurador se active.")
        return
    if args.add_to_steam:
        me = str(HERE / "framegrid.py")
        try:
            existing = [s for s in app.library() if s["type"] == "shortcut" and s["name"] == "FrameGrid"]
            if existing:
                print("FrameGrid ya está en la biblioteca de Steam.")
                return
            aid = app.add_shortcut("FrameGrid", me, str(HERE), "--open steam")
            print(f"FrameGrid añadido a Steam (appid {aid}).")
        except RuntimeError as e:
            print(e)
            sys.exit(1)
        return
    port = free_port(args.port)
    stop = threading.Event()
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app, stop))
    url = f"http://127.0.0.1:{port}/"
    print(f"FrameGrid {VERSION} en {url}  (Ctrl+C para salir)")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    open_ui(url, args.open)
    try:
        stop.wait()
    except KeyboardInterrupt:
        pass
    srv.shutdown()


if __name__ == "__main__":
    main()
