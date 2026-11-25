// FrameGrid — Copyright (C) 2026 Javier · SPDX-License-Identifier: GPL-3.0-or-later
// Traducciones de la interfaz. El texto original (clave) está en español.
// T("texto", {var}) devuelve la traducción del idioma activo; {var} se sustituye.
const I18N = {en: {
  // cabecera / estado
  "Steam…": "Steam…",
  "Activar modo en vivo": "Activate live mode",
  "Modo en vivo: reinicia la Frame": "Live mode: restart the Frame",
  "Abrir Steam": "Open Steam",
  "Ajustes": "Settings",
  "Cerrar FrameGrid": "Close FrameGrid",
  "Salir": "Quit",
  "sin usuario": "no user",
  "En vivo": "Live",
  "Steam cerrado · archivos": "Steam closed · files",
  "Sin modo en vivo": "No live mode",
  "Conectado al Steam abierto: los cambios se ven al momento.": "Connected to the running Steam: changes show up instantly.",
  "Steam está cerrado: FrameGrid edita sus archivos directamente.": "Steam is closed: FrameGrid edits its files directly.",
  "Steam está abierto pero su depurador CEF no está activo: solo se pueden guardar carátulas (se verán al reiniciar).":
    "Steam is running but its CEF debugger is not active: only artwork can be saved (it will show after a restart).",
  "Depurador CEF activado ({n} archivo). Reinicia la Steam Frame y vuelve a abrir FrameGrid: el indicador pasará a «En vivo».":
    "CEF debugger enabled ({n} file). Restart the Steam Frame and open FrameGrid again: the indicator will switch to \"Live\".",
  "Si tras reiniciar sigue sin modo en vivo: Ajustes de Steam › Sistema › Modo desarrollador, y luego Desarrollador › Depuración remota CEF.":
    "If live mode is still off after restarting: Steam Settings › System › Developer Mode, then Developer › CEF Remote Debugging.",
  "Abriendo Steam…": "Opening Steam…",
  "FrameGrid cerrado. Ya puedes cerrar esta pestaña.": "FrameGrid closed. You can close this tab now.",
  // lista
  "Filtrar biblioteca…": "Filter library…",
  "Todos": "All",
  "Solo con huecos": "Only with gaps",
  "Marcar todos": "Tick all",
  "Meter todos": "Add all",
  "Editando": "Editing",
  "Marca o desmarca juegos para meterlos o sacarlos. Se guarda al momento.": "Tick or untick games to add or remove them. Saved instantly.",
  "Terminar": "Done",
  "marcados": "ticked",
  "Sobrescribir existentes": "Overwrite existing",
  "Auto-rellenar desde SteamGridDB": "Auto-fill from SteamGridDB",
  "Nada por aquí.": "Nothing here.",
  "{n} juegos": "{n} games",
  "{n} juego": "{n} game",
  "«{c}»": "“{c}”",
  "Ya están todos dentro": "They are all in already",
  "¿Meter {n} juegos en «{c}»?": "Add {n} games to \"{c}\"?",
  // pestañas y carátulas
  "Carátulas": "Artwork",
  "Colecciones": "Collections",
  "Añadir no-Steam": "Add non-Steam",
  "Elige un juego o app de la lista.": "Pick a game or app from the list.",
  "Póster": "Capsule", "Horizontal": "Wide", "Héroe": "Hero", "Logo": "Logo", "Icono": "Icon",
  "transparente": "transparent", "cuadrado": "square",
  "vacío": "empty", "Quitar": "Remove", "Imagen quitada": "Image removed",
  "Mis imágenes": "My images",
  "Solo las que encajan": "Only fitting ones",
  "Abrir esta carpeta por defecto": "Open this folder by default",
  "Fijar carpeta": "Set folder",
  "Subir archivo…": "Upload file…",
  "Toca una imagen para instalarla en el hueco seleccionado arriba. Solo PNG y JPG.": "Click an image to apply it to the slot selected above. PNG and JPG only.",
  "Toca una imagen para instalarla en el hueco seleccionado arriba.": "Click an image to apply it to the slot selected above.",
  "Buscar en SteamGridDB": "Search SteamGridDB",
  "Nombre del juego": "Game name",
  "Buscar": "Search",
  "Animadas": "Animated",
  "Cargar más": "Load more",
  "Buscando…": "Searching…",
  "Sin resultados. Prueba con otro nombre.": "No results. Try another name.",
  "No hay imágenes de este tipo.": "No images of this type.",
  "Hueco actual: {l} ({d}).": "Current slot: {l} ({d}).",
  "encaja": "fits",
  " · no válido en Steam": " · not valid in Steam",
  "Ninguna imagen tiene la proporción de este hueco.": "No image has the shape of this slot.",
  "No hay imágenes en esta carpeta.": "No images in this folder.",
  "⬆ Carpeta anterior": "⬆ Parent folder",
  "Esta carpeta se abrirá por defecto": "This folder will open by default",
  "Imagen aplicada en Steam.": "Image applied in Steam.",
  "Imagen instalada. Se verá al abrir Steam.": "Image installed. It will show when Steam opens.",
  "Procesando {n}…": "Processing {n}…",
  "Auto-rellenado: {ok} correctos": "Auto-fill: {ok} done",
  ", {n} con problemas": ", {n} with problems",
  // colecciones
  "Colecciones de este equipo": "Collections on this device",
  "Nueva colección (p. ej. Ports, Mis juegos, Emuladores)": "New collection (e.g. Ports, My games, Emulators)",
  "Crear": "Create",
  "Las colecciones con apps no-Steam usan el appid local de cada acceso directo, por eso no se pueden preparar desde otro PC: hay que editarlas en la propia máquina. En modo en vivo los cambios los hace el propio Steam y se ven al momento.":
    "Collections with non-Steam apps use each shortcut's local appid, so they can't be prepared on another PC: they must be edited on the device itself. In live mode Steam makes the changes itself and they show up instantly.",
  "El modo en vivo no está activo: con Steam abierto no se pueden tocar colecciones ni accesos directos. Pulsa «Activar modo en vivo» arriba y reinicia la Steam Frame.":
    "Live mode is not active: with Steam running, collections and shortcuts can't be changed. Press \"Activate live mode\" above and restart the Steam Frame.",
  "Editando <b>{c}</b>: marca en la lista de la izquierda los juegos que quieras dentro. Pulsa «Terminar» cuando acabes.":
    "Editing <b>{c}</b>: tick the games you want in it in the list on the left. Press \"Done\" when you finish.",
  "Pulsa <b>Editar juegos</b> en una colección y marca sus juegos en la lista de la izquierda.":
    "Press <b>Edit games</b> on a collection and tick its games in the list on the left.",
  "dinámica (se edita en Steam)": "dynamic (edit it in Steam)",
  "Editar juegos": "Edit games", "Renombrar": "Rename", "Borrar": "Delete",
  "Favoritos": "Favorites", "Ocultos": "Hidden",
  "Nuevo nombre": "New name",
  "¿Borrar la colección «{c}»? Los juegos no se borran.": "Delete the collection \"{c}\"? The games are not deleted.",
  "Colección «{c}» creada. Ahora marca sus juegos en la lista.": "Collection \"{c}\" created. Now tick its games in the list.",
  "Colección creada": "Collection created",
  // añadir no-Steam
  "El modo en vivo no está activo: con Steam abierto no se pueden añadir accesos directos. Pulsa «Activar modo en vivo» arriba y reinicia la Steam Frame.":
    "Live mode is not active: with Steam running, shortcuts can't be added. Press \"Activate live mode\" above and restart the Steam Frame.",
  "Añadir app o juego no-Steam": "Add a non-Steam app or game",
  "Nombre": "Name", "Mi juego": "My game",
  "Ejecutable": "Executable",
  "/home/deck/Games/MiJuego/MiJuego.arm64": "/home/deck/Games/MyGame/MyGame.arm64",
  "Carpeta de inicio": "Start folder",
  "(vacío = carpeta del ejecutable)": "(empty = executable's folder)",
  "Opciones de lanzamiento": "Launch options",
  "Añadir a Steam": "Add to Steam",
  "Buscar carátulas al añadir": "Fetch artwork when adding",
  "Nombre y ejecutable son obligatorios": "Name and executable are required",
  "Añadido «{n}» (appid {id})": "Added \"{n}\" (appid {id})",
  "Carátulas: ": "Artwork: ",
  "Carátulas descargadas": "Artwork downloaded",
  // ajustes y API key
  "API key de SteamGridDB": "SteamGridDB API key",
  "pega aquí tu API key": "paste your API key here",
  "•••••• (guardada; escribe para cambiarla)": "•••••• (saved; type to change it)",
  "Pegar": "Paste",
  "Obtener clave en SteamGridDB": "Get key on SteamGridDB",
  "📱 Enviar desde el móvil (QR)": "📱 Send from phone (QR)",
  "Escanea este código con el móvil": "Scan this code with your phone",
  "Se abrirá una página donde pegar tu API key. El móvil tiene que estar en la misma red wifi que la Steam Frame.":
    "A page opens where you paste your API key. The phone must be on the same Wi-Fi network as the Steam Frame.",
  "Caduca en {s} s": "Expires in {s} s",
  "El código ha caducado. Pulsa de nuevo para generar otro.": "The code has expired. Press again to generate a new one.",
  "API key recibida desde el móvil ✓": "API key received from your phone ✓",
  "No se pudo leer el portapapeles: pega con Ctrl+V.": "Couldn't read the clipboard: paste with Ctrl+V.",
  "Comprobando la clave…": "Checking the key…",
  "Usuario de Steam": "Steam user",
  "Carpeta de Steam": "Steam folder",
  "(vacío = autodetectar)": "(empty = auto-detect)",
  "Detectada: {p}": "Detected: {p}",
  "ninguna": "none",
  "Cancelar": "Cancel",
  "Guardar": "Save",
  "Ajustes guardados": "Settings saved",
  // actualizaciones
  "Actualizaciones": "Updates",
  "Buscar actualizaciones al abrir FrameGrid": "Check for updates when FrameGrid opens",
  "Buscar ahora": "Check now",
  "Actualización disponible": "Update available",
  "Ver en GitHub": "View on GitHub",
  "Más tarde": "Later",
  "Actualizar ahora": "Update now",
  "⬆ Actualizar a {v}": "⬆ Update to {v}",
  "Ya tienes la última versión ({v}).": "You already have the latest version ({v}).",
  "Versión instalada: {a} → nueva: {b}": "Installed version: {a} → new: {b}",
  "FrameGrid se ejecuta desde un repositorio git: actualiza con «git pull».": "FrameGrid is running from a git repository: update it with \"git pull\".",
  "Descargando e instalando… no cierres FrameGrid.": "Downloading and installing… don't close FrameGrid.",
  "Instalado y verificado (SHA-256). Reiniciando FrameGrid…": "Installed and verified (SHA-256). Restarting FrameGrid…",
  "Instalado. Reiniciando FrameGrid…": "Installed. Restarting FrameGrid…",
  "FrameGrid no ha vuelto a arrancar solo. Ábrelo de nuevo desde el menú de aplicaciones.": "FrameGrid didn't restart by itself. Open it again from the application menu.",
}};

let LANG = "es";
function T(s, vars){
  let out = (LANG !== "es" && I18N[LANG] && I18N[LANG][s]) || s;
  if (vars) out = out.replace(/\{(\w+)\}/g, (m, k) => (vars[k] ?? m));
  return out;
}

// Traduce los textos fijos del HTML. Guarda el original para poder volver al español.
// Los elementos con data-noi18n (contenido dinámico) se saltan.
function translateDom(root){
  const walk = el => {
    if (el.nodeType === 1){
      if (el.hasAttribute("data-noi18n") || el.tagName === "SCRIPT" || el.tagName === "STYLE") return;
      for (const attr of ["placeholder", "title"]){
        if (!el.hasAttribute(attr)) continue;
        const key = "i18n_" + attr;
        if (!(key in el.dataset)) el.dataset[key] = el.getAttribute(attr);
        const orig = el.dataset[key];
        if (orig) el.setAttribute(attr, T(orig));
      }
      el.childNodes.forEach(walk);
    } else if (el.nodeType === 3){
      if (el.__es === undefined) el.__es = el.nodeValue;
      const raw = el.__es, txt = raw.trim();
      if (!txt) return;
      const lead = raw.match(/^\s*/)[0], trail = raw.match(/\s*$/)[0];
      el.nodeValue = lead + T(txt) + trail;
    }
  };
  walk(root);
  document.documentElement.lang = LANG;
}
