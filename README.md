# FrameGrid

**English** · [Español](README.es.md)

Custom library artwork from [SteamGridDB](https://www.steamgriddb.com) and library collections manager for **Steam Frame** (SteamOS on ARM). It also works on Steam Deck, Steam Machine and any Linux PC with Steam.

On Steam Frame there is no Decky Loader, the *Manage › Set custom artwork* option is missing, and collections you create on another PC do not include your non-Steam games. FrameGrid fixes all of that for the apps you build yourself, the ports you download, games installed by hand and any other non-Steam shortcut.

<p align="center">
  <img src="docs/screenshots/03-framegrid-artwork.png" alt="FrameGrid running on Steam Frame, showing the artwork slots of a non-Steam game" width="900">
  <br><em>FrameGrid running on Steam Frame: SteamGridDB artwork applied to a non-Steam game.</em>
</p>

## Before and after

| Before | After |
|:---:|:---:|
| <img src="docs/screenshots/01-library-before.png" alt="Steam Frame home with blank non-Steam capsules" width="440"> | <img src="docs/screenshots/02-library-after.png" alt="Steam Frame home with custom artwork" width="440"> |

<p align="center"><em>The Steam Frame home screen with non-Steam shortcuts, before and after applying artwork with FrameGrid.</em></p>

## Features

- **Artwork**: search SteamGridDB and apply a capsule (600×900), wide capsule (920×430), hero, logo or icon to Steam games and non-Steam shortcuts.
- **Your own images**: for games that are not on SteamGridDB, browse your Pictures folder or upload a PNG/JPG file. Images with the right shape for the selected slot are marked *fits*.
- **Auto-fill**: tick several games and fill every empty artwork slot with one click.
- **Icons**: for non-Steam shortcuts, and for Steam games in live mode.
- **Collections**: create, rename and delete collections, and add or remove games, including non-Steam shortcuts, from Favorites, Hidden or your own collections.
- **Add non-Steam apps**: add ports, Godot builds or any executable to your library, and optionally download artwork for them in the same step.
- **English and Spanish interface**: switch with the **ES | EN** buttons in the header.
- **Easy API key entry**: send it from your phone by scanning a QR code, paste it, or open the SteamGridDB page with one click.
- **Built-in updater**: FrameGrid tells you when a new version is out and updates itself with one click.
- **No dependencies**: only Python 3 and its standard library. No pacman, pip or compiling, and it runs on ARM64 and x86.
- **Controller-friendly local web UI** with large buttons. It opens in the desktop browser or in Steam's built-in browser.

## Requirements

- SteamOS (Steam Frame, Steam Deck, Steam Machine) or any Linux with Steam
- Python 3.9 or newer. It is already included in SteamOS.
- A free SteamGridDB API key: sign in at steamgriddb.com, then go to **Preferences → API**

## Installation

Switch the device to **Desktop Mode** and open a terminal (Konsole).

```bash
# Option A: download the latest release zip from the Releases page
unzip FrameGrid-*.zip
cd FrameGrid

# Option B: clone the repository
git clone https://github.com/Javigracia/FrameGrid.git
cd FrameGrid

bash install.sh
```

`install.sh` copies FrameGrid to `~/.local/share/framegrid` and adds it to the application menu and the desktop. Run `bash install.sh --uninstall` to remove it.

You can also run it without installing: `python3 framegrid.py`

## Updating

From version 0.5.0, FrameGrid checks GitHub for a new release when it opens. If there is one, an **⬆ Update to X.Y.Z** button appears in the header:

1. Press it to read what's new.
2. Press **Update now**. FrameGrid downloads the release, verifies its SHA-256 checksum, keeps a backup of your current version in `~/.local/share/framegrid-backups/` and restarts itself. The page reloads on its own.

It never updates without asking. Your API key and settings are kept. You can turn the check off, or check manually, in **Settings → Updates**. From a terminal: `python3 ~/.local/share/framegrid/framegrid.py --check-update` and `--update`.

> If you run FrameGrid from a **git clone**, it won't overwrite it: update with `git pull`. Versions older than 0.5.0 don't have the updater yet, so update to 0.5.0 manually once.

## Live mode (required on Steam Frame)

Steam cannot be closed on Steam Frame. FrameGrid therefore talks to the **running** Steam client through its built-in CEF debugger on `localhost:8080`, the same way Decky plugins do. In live mode every change is applied by Steam itself and shows up immediately, with no restart.

### Turn it on (only once)

1. Open FrameGrid and click **"Activate live mode"**. From a terminal you can run `python3 framegrid.py --enable-cef` instead. Either way, FrameGrid creates the file `~/.steam/steam/.cef-enable-remote-debugging`.
2. **Restart the Steam Frame.** The debugger only starts when Steam starts.
3. Open FrameGrid again. The indicator in the top-left corner should now read **"Live"**, in green.

   <img src="docs/screenshots/live-mode-indicator-en.png" alt="FrameGrid header with the green live mode indicator" width="300">


If it still does not switch after the restart, enable the debugger from Steam's settings instead: **System → Enable Developer Mode**, then **Developer → CEF Remote Debugging**, and restart again.

To check the current state from a terminal:

```bash
python3 ~/.local/share/framegrid/framegrid.py --status
```

### Optional: add FrameGrid to your Steam library

Once live mode is active:

```bash
bash install.sh --steam
```

FrameGrid then appears in your library, and launching it from there opens the interface in Steam's own browser.

### Working modes

FrameGrid picks the mode automatically and shows it in the top-left indicator.

| Indicator | When | What you can do |
|---|---|---|
| **Live** | Steam is running and the CEF debugger is active | Everything, applied instantly |
| **Steam closed · files** | Steam is not running, for example on a desktop PC | Everything, by editing `shortcuts.vdf`, the `grid` folder and `cloudstorage` directly |
| **No live mode** | Steam is running without the debugger | Artwork only. It is saved to the `grid` folder and appears **after restarting** the device. Collections and shortcuts are blocked until live mode is on. |

## Usage

1. **Language**: FrameGrid starts in your system language. Switch any time with the **ES | EN** buttons in the header; your choice is remembered.
2. **API key**: on first launch the **Settings** window opens. Typing a 32-character key in VR is painful, so there are three ways to enter it:
   - **📱 Send from phone (QR)** (easiest in VR): scan the QR code with your phone, paste your key on the page that opens and press *Send to FrameGrid*. The key appears in the headset and Settings close by themselves. The phone must be on the same Wi-Fi network as the Steam Frame.
   - **Paste**: if you copied the key in the Frame's browser, press *Paste*.
   - **Get key on SteamGridDB**: opens the SteamGridDB API page so you can copy it.

   <img src="docs/screenshots/api-key-qr-en.png" alt="Settings window with the QR code to send the API key from a phone" width="560">

   FrameGrid checks the key with SteamGridDB before saving it, so a mistyped key is caught right away. It is stored in `~/.config/framegrid/config.json` with permissions 600.
3. **Artwork**
   1. Pick a game in the left list. The *No-Steam*, *Steam* and *All* tabs filter the list.
   2. Choose a slot: *Capsule*, *Wide*, *Hero*, *Logo* or *Icon*.
   3. Click an image to apply it. The *Animated*, *Humor* and *NSFW* filters change which results are shown.
   4. **Not on SteamGridDB?** Switch to the *My images* tab. It opens your Pictures folder; browse into subfolders and click an image to apply it, or press *Upload file…* to pick any PNG/JPG. *Only fitting ones* hides images with the wrong shape for the slot, and *Set folder* makes the current folder open by default.
4. **Auto-fill**: tick several games, then press **"Auto-fill from SteamGridDB"**. Tick *Overwrite existing* to also replace artwork you already set.
5. **Collections** (*Collections* tab):
   1. To create one, type a name and press **Create**. It opens straight away in edit mode.
   2. To change an existing one, press **Edit games** next to it.
   3. While editing, a blue banner appears above the game list and each checkbox means "this game is in the collection". Tick or untick games; every change is saved immediately. *Add all* puts every game currently shown in the list into the collection, so you can filter first.
   4. Press **Done** when you are finished.

   <img src="docs/screenshots/04-framegrid-collections.png" alt="FrameGrid editing the Ports collection" width="800">

   <em>Editing the *Ports* collection: the ticked games on the left are in it.</em>

   <img src="docs/screenshots/05-ports-collection.png" alt="The Ports collection in the Steam Frame library" width="800">

   <em>The resulting *Ports* collection in the Steam Frame library, with its artwork.</em>

6. **Add a non-Steam app** (*Add non-Steam* tab): enter a name and the executable path. The start folder and launch options are optional.
7. Click **Quit** when you are done.

> Non-Steam shortcut IDs are local to each machine. That is why collections containing non-Steam apps cannot be prepared on another PC and must be edited on the device itself. FrameGrid does exactly that.

## Command-line options

```
python3 framegrid.py [--port 8787] [--open auto|xdg|steam|none] [--steam-root PATH]
python3 framegrid.py --status          # current mode and diagnostics
python3 framegrid.py --enable-cef      # enable the Steam debugger (then restart)
python3 framegrid.py --add-to-steam    # add FrameGrid to the Steam library
python3 framegrid.py --check-update    # check GitHub for a new version
python3 framegrid.py --update          # download and install the latest version
```

## Backups

In **live mode**, Steam applies every change through its own functions, exactly as if you made it in Steam's interface.

In **files mode** and **no-live mode**, FrameGrid makes backups first:

- Replaced or removed artwork: `userdata/<id>/config/grid/.framegrid-backup/`
- `shortcuts.vdf`: `config/shortcuts.vdf.framegrid-DATE.bak` (the last 10 are kept)
- Collections: `config/cloudstorage-framegrid-backups/original/`, which holds the state before the first change, plus the last 20 versions

## Security note

The CEF debugger lets any program running **on the device** control the Steam client. It is the same thing Decky Loader enables on Steam Deck. FrameGrid's own server only listens on `127.0.0.1` and rejects requests coming from other websites.

The **phone pairing** opens a second, temporary server on your local network, only while the QR code is on screen. Its address contains a random one-time code, and it closes as soon as it receives a valid key, after 5 minutes, or after 10 failed attempts. The key travels over your home Wi-Fi without encryption, so only use it on a network you trust; otherwise use *Paste*.

The **updater** only downloads from this repository's official releases over HTTPS. It checks the SHA-256 checksum published with each release, refuses zips with paths outside their folder, checks that the version inside matches the release, and only runs when you press *Update now*.

To turn the debugger off, delete `~/.steam/steam/.cef-enable-remote-debugging` and restart.

## Troubleshooting

| Problem | Fix |
|---|---|
| The indicator stays on *No live mode* after restarting | Check that the file `~/.steam/steam/.cef-enable-remote-debugging` exists, or enable *CEF Remote Debugging* in Steam's Developer settings. Run `--status`. |
| "Invalid SteamGridDB API key (401)" | Generate a new key on steamgriddb.com and send it again from *Settings* |
| The phone can't open the QR page | Make sure the phone and the Frame are on the same Wi-Fi network (not a guest network), and that the code hasn't expired. If it still fails, use *Paste* instead. |
| Artwork does not show (no-live mode) | Restart the device. Without live mode, Steam only reads the `grid` folder when it starts. |
| Steam is not detected | Use `--steam-root ~/.local/share/Steam`, or set the Steam folder in *Settings* |
| The browser does not open | Open `http://127.0.0.1:8787` manually, or use `--open steam` |

## How it works

- **Live mode**: a minimal Chrome DevTools Protocol client, written with the standard library, evaluates JavaScript in Steam's `SharedJSContext`. It uses the same functions as the Decky plugins: `SteamClient.Apps.SetCustomArtworkForApp`, `SetShortcutIcon` and `AddShortcut`, plus `collectionStore`.
- **Files mode**: a binary VDF reader/writer for `shortcuts.vdf`, artwork files in `config/grid`, and collections in `config/cloudstorage/cloud-storage-namespace-1.json`.
- WebP images are skipped because Steam does not load them from the grid folder. Animated artwork is downloaded as APNG.

## License

FrameGrid is free software released under the **GNU General Public License v3.0 or later**. See [LICENSE](LICENSE).

You can use, study, share and modify it. If you distribute FrameGrid or a modified version, you must release the full source code under the same GPLv3 license. Nobody can turn it into a closed product.

FrameGrid is and will stay free. If someone asks you to pay for it, you can get it here for free.

## Credits

- Artwork from [SteamGridDB](https://www.steamgriddb.com). Please support the site and its artists.
- QR codes generated with [QR Code generator library](https://www.nayuki.io/page/qr-code-generator-library) by Project Nayuki (MIT license, included in `fg/qrcodegen.py`).
- Inspired by [decky-steamgriddb](https://github.com/SteamGridDB/decky-steamgriddb) and SGDBoop.

FrameGrid is not affiliated with Valve or SteamGridDB. Steam and Steam Frame are trademarks of Valve Corporation.
