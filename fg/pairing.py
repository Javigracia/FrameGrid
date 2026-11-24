# FrameGrid — Copyright (C) 2026 Javier
# SPDX-License-Identifier: GPL-3.0-or-later
"""Emparejamiento temporal para meter la API key desde el móvil.

Abre un servidor pequeño en la red local, solo mientras dura el emparejamiento,
con una URL que lleva un código secreto de un solo uso. El móvil abre esa URL
(escaneando el QR), pega la clave y FrameGrid la recibe. El servidor se cierra
solo al recibir una clave válida, a los 5 minutos o tras 10 intentos fallidos.
"""
from __future__ import annotations

import html
import json
import secrets
import socket
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .qrcodegen import QrCode

TIMEOUT = 300
MAX_FAILS = 10
SGDB_API_PAGE = "https://www.steamgriddb.com/profile/preferences/api"


def lan_ip() -> str | None:
    """IP de esta máquina en la red local (no envía tráfico: UDP connect solo elige la interfaz)."""
    for probe in ("192.168.1.1", "10.0.0.1", "8.8.8.8"):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect((probe, 9))
                ip = s.getsockname()[0]
                if ip and not ip.startswith("127."):
                    return ip
        except OSError:
            continue
    return None


def qr_svg(text: str) -> str:
    qr = QrCode.encode_text(text, QrCode.Ecc.MEDIUM)
    n, border = qr.get_size(), 3
    parts = [f"M{x + border},{y + border}h1v1h-1z" for y in range(n) for x in range(n) if qr.get_module(x, y)]
    size = n + border * 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges">'
            f'<rect width="100%" height="100%" fill="#fff"/><path d="{" ".join(parts)}" fill="#000"/></svg>')


PAGE_TXT = {
    "es": dict(title="FrameGrid · API key", h="Envía tu API key a FrameGrid",
               p="Copia tu clave de SteamGridDB, pégala aquí y pulsa Enviar. Aparecerá en las gafas.",
               get="1. Abrir la página de la API de SteamGridDB", paste="Pegar", send="2. Enviar a FrameGrid",
               ph="Pega aquí tu API key", ok="✓ ¡Listo! Ya puedes volver a las gafas y cerrar esta página.",
               sending="Comprobando…", net="No se pudo conectar con FrameGrid. ¿Sigue abierto el código QR?"),
    "en": dict(title="FrameGrid · API key", h="Send your API key to FrameGrid",
               p="Copy your SteamGridDB key, paste it here and press Send. It will appear in the headset.",
               get="1. Open the SteamGridDB API page", paste="Paste", send="2. Send to FrameGrid",
               ph="Paste your API key here", ok="✓ Done! You can go back to the headset and close this page.",
               sending="Checking…", net="Could not reach FrameGrid. Is the QR code still open?"),
}


def phone_page(lang: str) -> str:
    t = {k: html.escape(v) for k, v in PAGE_TXT.get(lang, PAGE_TXT["en"]).items()}
    return f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{t['title']}</title>
<style>body{{margin:0;padding:24px 18px;background:#0f141b;color:#e6edf5;font:17px/1.45 system-ui,sans-serif}}
h1{{font-size:22px;margin:0 0 8px}}p{{color:#8b9bb0;margin:0 0 20px}}
a.b,button{{display:block;width:100%;box-sizing:border-box;text-align:center;padding:14px;border-radius:10px;font:inherit;
font-weight:600;border:1px solid #2a3544;background:#1e2733;color:#e6edf5;text-decoration:none;margin-bottom:12px}}
button.p{{background:#4fa3ff;border-color:#4fa3ff;color:#04121f}}
.row{{display:flex;gap:8px;margin-bottom:12px}}.row input{{flex:1}}.row button{{width:auto;margin:0;padding:14px 16px}}
input{{padding:14px;border-radius:10px;border:1px solid #2a3544;background:#0a0e13;color:#e6edf5;font:15px monospace;min-width:0}}
#msg{{margin-top:8px;font-weight:600}}.ok{{color:#4cc38a}}.err{{color:#ef6461}}</style></head><body>
<h1>{t['h']}</h1><p>{t['p']}</p>
<a class="b" href="{SGDB_API_PAGE}" target="_blank" rel="noopener">{t['get']}</a>
<div class="row"><input id="k" placeholder="{t['ph']}" autocomplete="off" autocapitalize="off" spellcheck="false">
<button id="pa">{t['paste']}</button></div>
<button class="p" id="go">{t['send']}</button><div id="msg"></div>
<script>
const k=document.getElementById('k'),m=document.getElementById('msg');
document.getElementById('pa').onclick=async()=>{{try{{k.value=(await navigator.clipboard.readText()).trim()}}catch(e){{k.focus()}}}};
document.getElementById('go').onclick=async()=>{{
  const v=k.value.trim(); if(!v){{k.focus();return}}
  m.className='';m.textContent='{t['sending']}';
  try{{const r=await fetch(location.pathname,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{api_key:v}})}});
    const j=await r.json(); if(j.ok){{m.className='ok';m.textContent='{t['ok']}';k.value='';}}
    else{{m.className='err';m.textContent=j.error||('HTTP '+r.status)}}}}
  catch(e){{m.className='err';m.textContent='{t['net']}'}}
}};
</script></body></html>"""


class Pairing:
    """Una sesión de emparejamiento cada vez."""

    def __init__(self, on_key, tr):
        self.on_key = on_key      # callback(api_key) -> None o lanza excepción con el motivo
        self.tr = tr              # tr(msg, lang)
        self.lock = threading.Lock()
        self.srv = None
        self.token = None
        self.url = None
        self.expires = 0
        self.fails = 0
        self.done = False
        self.lang = "es"

    def status(self) -> dict:
        with self.lock:
            active = self.srv is not None and time.time() < self.expires
            return {"active": active, "done": self.done, "url": self.url if active else None,
                    "remaining": max(0, int(self.expires - time.time())) if active else 0}

    def start(self, lang: str, port: int = 8790) -> dict:
        self.stop()
        ip = lan_ip()
        if not ip:
            raise RuntimeError("No encuentro la dirección de red local de este equipo.")
        with self.lock:
            self.token = secrets.token_urlsafe(16)
            self.fails, self.done, self.lang = 0, False, lang
            srv = None
            for p in range(port, port + 30):
                try:
                    srv = ThreadingHTTPServer(("0.0.0.0", p), self._handler())
                    break
                except OSError:
                    continue
            if not srv:
                raise RuntimeError("No hay puertos libres")
            self.srv = srv
            self.url = f"http://{ip}:{srv.server_address[1]}/p/{self.token}"
            self.expires = time.time() + TIMEOUT
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            threading.Timer(TIMEOUT + 1, self._expire, args=(srv,)).start()
        return self.status()

    def _expire(self, srv):
        with self.lock:
            if self.srv is srv:
                self._close()

    def _close(self):
        srv, self.srv, self.token = self.srv, None, None
        if srv:
            threading.Thread(target=lambda: (srv.shutdown(), srv.server_close()), daemon=True).start()

    def stop(self):
        with self.lock:
            self._close()

    def qr(self) -> str | None:
        st = self.status()
        return qr_svg(st["url"]) if st["active"] else None

    def _handler(self):
        pairing = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, body, ctype):
                b = body.encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(b)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Referrer-Policy", "no-referrer")
                self.end_headers()
                self.wfile.write(b)

            def _token_ok(self):
                path = urllib.parse.urlparse(self.path).path
                with pairing.lock:
                    tok, live = pairing.token, time.time() < pairing.expires
                return bool(tok) and live and secrets.compare_digest(path, f"/p/{tok}")

            def do_GET(self):
                if not self._token_ok():
                    return self._send(404, "Not found", "text/plain")
                self._send(200, phone_page(pairing.lang), "text/html; charset=utf-8")

            def do_POST(self):
                if not self._token_ok():
                    return self._send(404, json.dumps({"ok": False, "error": pairing.tr(
                        "Código de emparejamiento no válido o caducado.", pairing.lang)}), "application/json")
                try:
                    n = min(int(self.headers.get("Content-Length") or 0), 4096)
                    key = (json.loads(self.rfile.read(n) or b"{}").get("api_key") or "").strip()
                    pairing.on_key(key)
                except Exception as e:
                    with pairing.lock:
                        pairing.fails += 1
                        too_many = pairing.fails >= MAX_FAILS
                        if too_many:
                            pairing._close()
                    return self._send(400, json.dumps({"ok": False, "error": pairing.tr(str(e), pairing.lang)}),
                                      "application/json")
                with pairing.lock:
                    pairing.done = True
                    pairing._close()
                self._send(200, json.dumps({"ok": True}), "application/json")

        return H
