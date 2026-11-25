# FrameGrid — Copyright (C) 2026 Javier
# SPDX-License-Identifier: GPL-3.0-or-later
"""Traducción al inglés de los mensajes del servidor (el código los genera en español).

Cada entrada es (expresión regular sobre el texto en español, plantilla en inglés).
Los grupos capturados se insertan con {0}, {1}...
"""
from __future__ import annotations

import re

_EN = [
    # cdp.py
    (r"El depurador de Steam cerró la conexión", "The Steam debugger closed the connection"),
    (r"Steam rechazó la conexión WebSocket: (.*)", "Steam rejected the WebSocket connection: {0}"),
    (r"Conexión con Steam perdida", "Lost connection to Steam"),
    (r"Steam cerró la conexión", "Steam closed the connection"),
    (r"Depurador de Steam no disponible en (\S+) \((.*)\)", "Steam debugger not available at {0} ({1})"),
    (r"Steam responde pero no encuentro su SharedJSContext", "Steam responds but its SharedJSContext was not found"),
    (r"Error dentro de Steam: Error: Colección no encontrada", "Error inside Steam: collection not found"),
    (r"Error dentro de Steam: Error: Las colecciones dinámicas se editan desde Steam\.",
     "Error inside Steam: dynamic collections are edited in Steam."),
    (r"Error dentro de Steam: (.*)", "Error inside Steam: {0}"),
    # imgutil.py
    (r"Solo se pueden usar imágenes de tu carpeta personal\.", "Only images inside your home folder can be used."),
    (r"No existe la carpeta (.*)", "Folder does not exist: {0}"),
    # sgdb.py
    (r"API key de SteamGridDB no válida \(401\)\.", "Invalid SteamGridDB API key (401)."),
    (r"SteamGridDB respondió (\d+)", "SteamGridDB returned {0}"),
    (r"Sin conexión con SteamGridDB: (.*)", "Cannot reach SteamGridDB: {0}"),
    # collections.py / live.py
    (r"Cierra Steam antes de editar colecciones: las tiene en memoria y las sobrescribe\.",
     "Close Steam before editing collections: it keeps them in memory and overwrites them."),
    (r"Colección no encontrada: (.*)", "Collection not found: {0}"),
    (r"No se pueden borrar Favoritos/Ocultos\.", "Favorites/Hidden cannot be deleted."),
    (r"Las colecciones dinámicas se editan desde Steam\.", "Dynamic collections are edited in Steam."),
    # steam.py
    (r"Cierra Steam antes de modificar shortcuts\.vdf \(Steam lo sobrescribe al salir\)\.",
     "Close Steam before changing shortcuts.vdf (Steam overwrites it on exit)."),
    # framegrid.py
    (r"No encuentro la instalación de Steam \(carpeta userdata\)\.", "Steam installation not found (userdata folder)."),
    (r"No hay usuarios en Steam/userdata\. Inicia sesión en Steam una vez\.",
     "No users in Steam/userdata. Sign in to Steam once."),
    (r"Falta la API key de SteamGridDB \(Ajustes\)\.", "SteamGridDB API key missing (Settings)."),
    (r"Steam está abierto y su depurador CEF no está activo\..*",
     "Steam is running and its CEF debugger is not active. Press \"Activate live mode\" and restart the "
     "Steam Frame (or enable Settings › Developer › CEF Remote Debugging)."),
    (r"Steam no carga WebP desde la carpeta grid; elige una imagen PNG/JPG\.",
     "Steam does not load WebP from the grid folder; pick a PNG/JPG image."),
    (r"Cambiar el icono de un juego de Steam necesita el modo en vivo\.",
     "Changing the icon of a Steam game requires live mode."),
    (r"Steam no da el icon_hash de este juego\.", "Steam does not provide this game's icon_hash."),
    (r"Icono guardado\. Se vinculará al acceso directo cuando actives el modo en vivo\.",
     "Icon saved. It will be linked to the shortcut once live mode is active."),
    (r"Guardada en la carpeta grid: se verá cuando reinicies la Steam Frame\.",
     "Saved to the grid folder: it will show after you restart the Steam Frame."),
    (r"El archivo no es una imagen PNG o JPG\.", "The file is not a PNG or JPG image."),
    (r"Steam no carga imágenes (\w+)\. Conviértela a PNG o JPG\.", "Steam does not load {0} images. Convert it to PNG or JPG."),
    (r"La imagen es demasiado grande \(máx\. 40 MB\)\.", "The image is too large (max. 40 MB)."),
    (r"Para restaurar el icono original de un juego de Steam, verifica sus archivos\.",
     "To restore a Steam game's original icon, verify its files."),
    (r"Sin resultados en SteamGridDB", "No results on SteamGridDB"),
    (r"No hay puertos libres", "No free ports"),
    (r"No se pudo comprobar la clave ahora mismo; se ha guardado igualmente\.",
     "Could not verify the key right now; it has been saved anyway."),
    # actualizador
    (r"GitHub respondió (\d+)", "GitHub returned {0}"),
    (r"Sin conexión con GitHub: (.*)", "Cannot reach GitHub: {0}"),
    (r"FrameGrid se ejecuta desde un repositorio git: actualiza con «git pull»\.",
     "FrameGrid is running from a git repository: update it with \"git pull\"."),
    (r"Ya tienes la última versión\.", "You already have the latest version."),
    (r"La descarga es demasiado grande\.", "The download is too large."),
    (r"La suma de verificación SHA-256 no coincide: actualización cancelada\.",
     "The SHA-256 checksum does not match: update cancelled."),
    (r"El zip descargado no tiene la estructura de FrameGrid\.", "The downloaded zip does not have FrameGrid's structure."),
    (r"La versión del zip no coincide con la de la release\.", "The zip's version does not match the release."),
    (r"install\.sh falló: (.*)", "install.sh failed: {0}"),
    (r"El zip contiene rutas no permitidas: actualización cancelada\.", "The zip contains forbidden paths: update cancelled."),
    # emparejamiento
    (r"Código de emparejamiento no válido o caducado\.", "Invalid or expired pairing code."),
    (r"No encuentro la dirección de red local de este equipo\.", "Could not find this device's local network address."),
]
_EN = [(re.compile("^" + p + "$", re.S), t) for p, t in _EN]


def tr(msg: str | None, lang: str | None) -> str | None:
    if not msg or lang != "en":
        return msg
    for rx, tpl in _EN:
        m = rx.match(msg)
        if m:
            return tpl.format(*m.groups())
    return msg
