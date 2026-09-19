# No Man's Sky - Discovery Cache Bug Fix

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