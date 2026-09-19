# NMS Discovery Optimizer

A lightweight, standalone Windows tool to clean up your bloated No Man's Sky discovery cache and unlock Paradise Quotient rankings. No Python or installation required.

## Features
* **Wipe Hidden Systems:** Permanently delete systems you previously hid in-game.
* **Targeted Foreign Data Cleanup:** Selectively remove Flora, Fauna, Minerals, or Planets discovered by other players to reduce save file bloat.
* **Paradise Quotient Injection:** Automatically formats and injects all your discovered planets into the Wonders record so the game engine calculates their true Paradise Quotient.

## Requirements
* [Goatfungus NMSSaveEditor](https://github.com/goatfungus/NMSSaveEditor) (Required to safely decrypt/encrypt the save file).

## How to Use
1. **Export:** Open Goatfungus NMSSaveEditor, load your save slot, and go to **Edit -> Export JSON**. Save the file to your computer.
2. **Run:** Download and open `gui_optimizer.exe` from the [Releases](https://github.com/August1879/nms-discovery-bug-fix/releases) tab.
3. **Select:** Click **Browse** to select your exported JSON file and type in your exact in-game username.
4. **Optimize:** Check the boxes for the optimizations you want and click **Optimize Save**. 
5. **Import:** Return to Goatfungus, go to **Edit -> Import JSON**, select the new `optimized_save.json`, and save your changes. 

## Download
Grab the latest `.exe` from the [Releases](https://github.com/August1879/nms-discovery-bug-fix/releases) page.
