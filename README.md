# NMS Discovery Optimizer

A lightweight, powerful tool to clean up your No Man's Sky save file by removing bloated, foreign discovery data. This tool drastically reduces your save file size, fixing memory overflow issues and disappearing discoveries.

## 📖 Step-by-Step Usage Guide

**Step 1: Export your Save to JSON**
1. Download and open the **[Goatfungus No Man's Sky Save Editor](https://github.com/goatfungus/NMSSaveEditor)**.
2. Select the save slot you want to optimize.
3. In the top menu bar, click **Edit** -> **Edit JSON**.
4. A text window will open. Click the **Export** button at the bottom and save the `.json` file to your desktop. 

**Step 2: Optimize the Data**
1. Download the latest version of the NMS Discovery Optimizer from the Releases page and run it.
2. Click **Browse** and select the `.json` file you just exported.
3. Enter your exact in-game Username.
4. Select what you want to remove (Foreign Flora/Fauna/Minerals, Hidden Systems, or All Foreign Discoveries).
5. Click **Optimize Save**. The tool will instantly clean the file and create a byte-for-byte backup of your original.

**Step 3: Import the Cleaned Save**
1. Go back to the Goatfungus JSON Editor window.
2. Click **Import** and select the newly optimized JSON file.
3. Close the JSON window, click **Save Changes** in the main editor, and launch your game!

---

## 🛠️ Troubleshooting & Notes

* **Goatfungus 0kb Export Crash:** If Goatfungus spits out a 0kb file or crashes when exporting a massive save, it has run out of RAM. Launch Goatfungus from your command line using this command to give it more memory: 
  `java -Xmx1G -jar NMSSaveEditor.jar`
* **Linux/Wine Compatibility:** Because this tool is packaged as a Windows `.exe` with an embedded Python interpreter, Wine sometimes fails to launch it. A native Python script version for Linux may be provided in the future.

---

## What's New in v1.1.7
* **Universal JSON Escape Sanitizer:** The tool now mimics the No Man's Sky game engine, automatically neutralizing any corrupted multiplayer Comm Ball data or invalid hex codes (like `\x` or `\e`) into plain text without crashing.
* **Built-in Auto-Updater:** The tool silently checks GitHub on launch and alerts you when a new version is available.
* **Pre-Write Safety:** Creates a byte-for-byte backup and ensures the JSON output only publishes if the write is completed without interruption.

---

## 🌌 Join My Alliance!
**I have discovered a pristine, undiscovered Earth-like planet and claimed the local station.** 
I am currently recruiting players to colonize the system and build a massive hub alliance. 

* **[View the Planet & Portal Glyphs on Reddit](https://www.reddit.com/r/NoMansSkyTheGame/s/LTUupn3YrA)**
* **[Message me on Discord to join](https://discord.com/users/1082971394968657920)**
