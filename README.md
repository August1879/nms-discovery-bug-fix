# No Man's Sky - Discovery Cache Bug Fix

**Version 1.0**

## The Problem
In *No Man's Sky*, the local save file has a hard cap (around 3,250 records) for storing discovered systems, flora, fauna, and minerals. Once this cache fills up with multiplayer data, the game stops permanently recording your new personal discoveries locally.

## The Solution
This Python script filters your `save.hg` raw JSON data, safely wiping out multiplayer cache entries while permanently preserving your own personal discoveries.

## How to Use
1. Download the [Goatfungus NMSSaveEditor](https://github.com/goatfungus/NMSSaveEditor).
2. Open your main save file, go to **Edit** -> **Edit Raw JSON**, and expand `DiscoveryManagerData`.
3. Copy the entire `DiscoveryData-v1` JSON block and save it in the same folder as the script as `discoveries.json`.
4. Open `fix_cache.py` and change `"YOUR_IN_GAME_NAME"` to your exact in-game username.
5. Run the script: `python fix_cache.py`
6. Paste the contents of the generated `discoveries_fixed.json` back over the `DiscoveryData-v1` block in the save editor and save your changes.

**Version 1.1**

# No Man's Sky: Hidden System Cleaner

## What This Does
In *No Man's Sky*, when you press the **F** key to "Hide" a system from your Discoveries list, the game does not actually delete the data. Instead, it attaches a hidden `"F": 1` flag to the system and leaves it sitting in your save file. Over time, these "ghost" systems bloat your `DiscoveryManagerData` cache. 

This Python script safely scans your raw save data, targets every system flagged with `"F": 1`, and permanently deletes them from the cache. This permanently clears your removed systems list and optimizes your save file.

## Prerequisites
* Python 3.x installed on your system.
* [Goatfungus NMS Save Editor](https://github.com/goatfungus/NMSSaveEditor).

## Step-by-Step Guide

**Step 1: Export Your Save Data**
1. Open the Goatfungus NMS Save Editor and select your save slot.
2. **Crucial:** Make a manual backup of your save file using the save editor's backup feature.
3. Go to the top menu and select **Edit** -> **Export JSON**.
4. Name the file `full_save.json` and save it in the exact same folder as the Python script.

**Step 2: Run the Cleanup Script**
1. Open your terminal or command prompt.
2. Navigate to the folder containing the script and your save file.
3. Run the script:
   `python clean_hidden.py`
4. The terminal will output how many hidden systems were found and wiped. It will generate a new file called `clean_save.json`.

**Step 3: Import the Cleaned Save**
1. Go back to the Goatfungus Save Editor.
2. Select **Edit** -> **Import JSON** and choose the new `clean_save.json` file.
3. Click the main **Save** button in the Goatfungus UI to overwrite your game save.
4. Boot up No Man's Sky. Your removed systems will be permanently gone.

## Troubleshooting / Common Errors

* **`FileNotFoundError: [Errno 2] No such file or directory: 'full_save.json'`**
  You either haven't exported the JSON from Goatfungus yet, or it was saved in the wrong folder. Ensure `full_save.json` is in the exact same directory as `clean_hidden.py`.

* **JSON Parsing Errors / Invalid Escape Characters**
  No Man's Sky saves often contain illegal backslash characters that crash standard JSON parsers. This script features a built-in memory sanitizer to bypass this, but if it still crashes, ensure you exported a fresh JSON directly from Goatfungus without making manual edits first.

* **The Game Crashes on Load or Shows Corrupted Save**
  This usually means the JSON formatting got warped. Do not panic. Close the game, open Goatfungus, and restore the backup you made in Step 1.