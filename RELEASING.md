# Releasing a new version

The built-in updater depends on these steps. Keep the names exactly as shown.

1. **Bump the version** in `framegrid.py` (`VERSION = "X.Y.Z"`). The updater refuses a zip whose version doesn't match the release tag.
2. **Build the zip** so it contains the `FrameGrid` folder, named `FrameGrid-X.Y.Z.zip`. On macOS, from the folder that contains `FrameGrid`:

   ```bash
   zip -r -X FrameGrid-X.Y.Z.zip FrameGrid -x "*.DS_Store" "*/__pycache__/*" "*/.git/*"
   ```

3. **Create the checksum file**:

   ```bash
   shasum -a 256 FrameGrid-X.Y.Z.zip > FrameGrid-X.Y.Z.zip.sha256
   ```

4. **Create the GitHub release** with tag `vX.Y.Z` and attach **both** files: `FrameGrid-X.Y.Z.zip` and `FrameGrid-X.Y.Z.zip.sha256`.
5. Publish it as a **normal release**. Don't mark it as a pre-release or leave it as a draft: the updater only sees the release GitHub marks as *Latest*.

The release notes you write are shown to users inside FrameGrid before they update. Bold text, `code` and `-` bullet lists are displayed nicely.

Keep two-factor authentication enabled on the GitHub account: whoever can publish releases here can push updates to every FrameGrid installation.
