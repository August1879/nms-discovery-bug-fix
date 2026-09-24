# NMS Discovery Optimizer

A lightweight, powerful tool to clean up your No Man's Sky save file by removing bloated, foreign discovery data. This tool drastically reduces your save file size, fixing memory overflow issues and disappearing discoveries.

## What's New in v1.1.4
* **Built-in Auto-Updater:** The tool now silently checks GitHub on launch and alerts you when a new version is available.
* **Smart Diagnostics:** Automatically detects 0-byte Save Editor memory crashes and provides exact terminal commands to allocate more RAM to Goatfungus.
* **Legacy Ship Protection:** Added explicit UI warnings to prevent NomNom from corrupting legacy Atlas Rises ships during the import phase.
* **Bulletproof JSON Parsing:** Completely overhauled backend with strict UTF-8 parsing, ensuring complex nested base data is never mangled.
* **Pre-Write Safety:** Creates a byte-for-byte backup and ensures the JSON output only publishes if the write is completed without interruption.

---

## 🌌 Join My Alliance!
**I have discovered a pristine, undiscovered Earth-like planet and claimed the local station.** 
I am currently recruiting players to colonize the system and build a massive hub alliance. 

If you are looking for a permanent home system with perfect weather and an active community, come build your base with us! 
**[Click here to get the Portal Glyphs and join the Alliance!]** *(Note: Add your actual link here in the markdown)*

---

## Acknowledgements
A massive thank you to **magrhino** for their incredible Pull Request! They completely re-engineered the backend architecture, added robust UTF-8 parsing safety, implemented automated regression testing, and built the pre-write verification system to ensure this tool meets professional software standards.
