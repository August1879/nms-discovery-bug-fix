# NMS Discovery Optimizer v1.1.3

A lightweight, standalone Windows tool to clean up your bloated No Man's Sky discovery cache, fix infinite loading glitches, and unlock Paradise Quotient rankings. 

## Features
* **Targeted Foreign Data Cleanup:** Selectively remove Flora, Fauna, Minerals, or Planets discovered by other players.
* **Wipe Hidden Systems:** Permanently delete systems you previously hid in-game.
* **Paradise Quotient Injection:** Automatically formats and injects your discovered planets into the Wonders record to calculate true Paradise Quotients.
* **Whitelist Protection:** Enter comma-separated usernames or system names to strictly protect them from deletion (uses exact-match logic to prevent false positives).
* **Automated Memory Allocation:** Dynamically recalculates and overwrites your `ReserveStore` and `ReserveManaged` headers to prevent game crashes upon loading.
* **Smart Encoding & Safeguards:** Automatically handles Windows BOM hidden characters and blocks execution if the Save Editor provides an empty file.
* **Automatic Backups:** Safely creates a timestamped `.bak` copy of your JSON file before any modifications are made.

## Requirements
* [Goatfungus NMSSaveEditor](https://github.com/goatfungus/NMSSaveEditor) OR [NomNom Save Editor](https://github.com/cengelha/NomNom) (Required to safely decrypt/encrypt the save file).

## How to Use
1. **Export:** Open your Save Editor, load your save slot, and go to **Edit -> Export JSON**. Save the file to your computer.
   * *Note: If you have a massive legacy save file (7+ years old) and Goatfungus exports a blank 0-byte file, use NomNom for this step instead.*
2. **Run:** Download and open `gui_optimizer.exe` from the [Releases](https://github.com/August1879/nms-discovery-bug-fix/releases) tab.
3. **Select:** Click **Browse** to select your exported JSON file and type in your exact in-game username.
4. **Whitelist (Optional):** Enter the exact names of any players or systems you want to keep.
5. **Optimize:** Check your desired cleanup options and click **Optimize Save**. 
6. **Import:** Return to your Save Editor, go to **Edit -> Import JSON**, select the new `optimized_save.json`, and save your changes. 

## Download
Grab the latest `.exe` from the [Releases](https://github.com/August1879/nms-discovery-bug-fix/releases) page.
