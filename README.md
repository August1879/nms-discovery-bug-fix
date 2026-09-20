# NMS Discovery Optimizer

A lightweight, standalone Windows tool to clean up your bloated No Man's Sky discovery cache and unlock Paradise Quotient rankings. 

## Features
* **Wipe Hidden Systems:** Permanently delete systems you previously hid in-game.
* **Targeted Foreign Data Cleanup:** Selectively remove Flora, Fauna, Minerals, or Planets discovered by other players.
* **Paradise Quotient Injection:** Automatically formats and injects your discovered planets into the Wonders record to calculate true Paradise Quotients.
* **Whitelist Protection (New):** Enter comma-separated usernames or system names to strictly protect them from deletion.
* **Automatic Backups (New):** Safely creates a timestamped `.bak` copy of your JSON file before any modifications are made.
* **Activity Log (New):** Real-time terminal readout detailing exactly how many records were wiped, protected, or injected.
* **Dark Theme UI (New):** Sleek modern interface that is easy on the eyes.

## Requirements
* [Goatfungus NMSSaveEditor](https://github.com/goatfungus/NMSSaveEditor) (Required to safely decrypt/encrypt the save file).

## How to Use
1. **Export:** Open Goatfungus NMSSaveEditor, load your save slot, and go to **Edit -> Export JSON**. Save the file to your computer.
2. **Run:** Download and open `gui_optimizer.exe` from the [Releases](https://github.com/August1879/nms-discovery-bug-fix/releases) tab.
3. **Select:** Click **Browse** to select your exported JSON file and type in your exact in-game username.
4. **Whitelist (Optional):** Enter the names of any players or systems you want to keep.
5. **Optimize:** Check your desired cleanup options and click **Optimize Save**. 
6. **Import:** Return to Goatfungus, go to **Edit -> Import JSON**, select the new `optimized_save.json`, and save your changes. 

## Download
Grab the latest `.exe` from the [Releases](https://github.com/August1879/nms-discovery-bug-fix/releases) page.
