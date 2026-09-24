# NMS Discovery Optimizer

A Windows tool for editing discovery records in JSON exported from a No Man's Sky save editor.

## Features
* **Targeted Foreign Data Cleanup:** Selectively remove Flora, Fauna, Minerals, or Planets discovered by other players.
* **Wipe Hidden Systems:** Optionally delete hidden system records, including your own. This option starts off.
* **Paradise Quotient Injection:** Automatically formats and injects your discovered planets into the Wonders record to calculate true Paradise Quotients.
* **Record Whitelist:** Enter comma-separated usernames or record names to protect matching records from deletion. A system name does not automatically protect its planets, plants, animals, or minerals.
* **Reserve Counters:** Sets `ReserveStore` and `ReserveManaged` to the remaining record count when records are removed. Game compatibility still needs validation with your save editor and game version.
* **Strict JSON Parsing:** Accepts UTF-8 JSON with or without a BOM and stops on invalid encoding or JSON.
* **Original Export Backup:** After you approve a change, creates a byte-for-byte timestamped `.json` backup beside the export. Existing output files are never overwritten.

## Requirements
* [Goatfungus NMSSaveEditor](https://github.com/goatfungus/NMSSaveEditor) OR [NomNom Save Editor](https://github.com/cengelha/NomNom) (Required to safely decrypt/encrypt the save file).

## How to Use
1. **Export:** Open your Save Editor, load your save slot, and go to **Edit -> Export JSON**. Save the file to your computer.
   * *Note: If you have a massive legacy save file (7+ years old) and Goatfungus exports a blank 0-byte file, use NomNom for this step instead.*
2. **Run:** Run `python gui_optimizer.py` from this branch with Python 3.11 or later and Tkinter. The upstream v1.1.3 executable does not include these fixes.
3. **Select:** Click **Browse** to select your exported JSON file and type in your in-game username. The tool stops if no discovery record matches it (case-insensitively). If older records use another username, protect those usernames with the whitelist and review every proposed deletion.
4. **Whitelist (Optional):** Enter exact record names or usernames you want to protect. Matches are case-insensitive and apply to each record individually.
5. **Optimize:** Choose cleanup options, click **Optimize Save**, and review the complete list of records to remove and Paradise records to add before approving the write.
6. **Import:** Compare the output with your export, then return to your Save Editor and import the new `optimized_save.json`. If that output name already exists, move or rename it before running the tool again.

Keep an independent copy of the native save folder and original JSON export before importing any result. The backup created by this tool covers only the selected JSON export. Reserve-counter and Paradise-record changes have not been validated against every game or save-editor version.

## Windows executable
To build an executable with these fixes, run `pyinstaller --onefile --windowed gui_optimizer.py` from this branch on Windows. The upstream [Releases](https://github.com/August1879/nms-discovery-bug-fix/releases) page contains the older build.
