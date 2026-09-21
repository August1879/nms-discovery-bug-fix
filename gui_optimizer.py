import json
import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filepath)

def log_message(log_widget, message):
    log_widget.config(state=tk.NORMAL)
    log_widget.insert(tk.END, message + "\n")
    log_widget.see(tk.END)
    log_widget.config(state=tk.DISABLED)
    log_widget.update()

def optimize_save(log_widget):
    filepath = file_entry.get().strip()
    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Please select a valid full_save.json file.")
        return

    username = user_entry.get().strip()
    if not username:
        messagebox.showerror("Error", "Please enter your in-game username.")
        return

    # Parse whitelist inputs
    whitelist_raw = whitelist_entry.get().strip()
    whitelisted_names = {w.strip().lower() for w in whitelist_raw.split(",") if w.strip()}

    wipe_hidden = var_hidden.get()
    wipe_fauna = var_fauna.get()
    wipe_flora = var_flora.get()
    wipe_mineral = var_mineral.get()
    wipe_all = var_all.get()
    inject_paradise = var_paradise.get()

    if not any([wipe_hidden, wipe_fauna, wipe_flora, wipe_mineral, wipe_all, inject_paradise]):
        messagebox.showwarning("Warning", "Please select at least one optimization option.")
        return

    try:
        # Clear log
        log_widget.config(state=tk.NORMAL)
        log_widget.delete(1.0, tk.END)
        log_widget.config(state=tk.DISABLED)
        
        log_message(log_widget, "--- Starting Optimization Process ---")
        log_message(log_widget, "Loading and sanitizing save file...")
        
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()

        if not content.strip():
            log_message(log_widget, "ERROR: The file is completely empty.")
            messagebox.showerror("Error", "The selected JSON file is empty (0 bytes). The Save Editor failed to export your save data.")
            return

        content = content.replace('\\', '\\\\').replace('\\\\"', '\\"')

        content = content.replace('\\', '\\\\').replace('\\\\"', '\\"')
        content = "".join(ch for ch in content if ord(ch) >= 32 or ch in '\n\r\t')
        data = json.loads(content, strict=False)

        # Automatic Timestamped Backup
        backup_filename = f"full_save_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(os.path.dirname(filepath), backup_filename)
        log_message(log_widget, f"Creating safety backup: {backup_filename}")
        with open(backup_path, "w", encoding="utf-8") as backup_file:
            backup_file.write(content)

        records = data.get("DiscoveryManagerData", {}).get("DiscoveryData-v1", {}).get("Store", {}).get("Record", [])
        ps = data.get("BaseContext", {}).get("PlayerStateData", {})
        
        # Prep for Paradise Injection
        existing_wonders = ps.get("WonderPlanetRecords", [])
        existing_ids = set()
        for w in existing_wonders:
            gen_id = w.get("GenerationID", [])
            if len(gen_id) == 2:
                existing_ids.add((gen_id[0], gen_id[1]))

        cleaned_records = []
        removed_count = 0
        whitelisted_skipped = 0
        new_wonders = []

        log_message(log_widget, "Scanning discovery records...")
        for r in records:
            dt = r.get("DD", {}).get("DT", "")
            usn = r.get("OWS", {}).get("USN", "")
            record_name = r.get("DD", {}).get("N", "").lower()
            
            is_hidden = r.get("FL", {}).get("F") == 1
            is_foreign = (usn != username and usn != "")
            is_mine = (usn == username)

            # BUG FIX v1.1.2: Exact match instead of substring match to prevent false positives
            is_whitelisted = False
            if whitelisted_names:
                if usn.lower() in whitelisted_names or record_name in whitelisted_names:
                    is_whitelisted = True

            # Paradise Logic
            if inject_paradise and dt == "Planet" and is_mine:
                ua = r.get("DD", {}).get("UA")
                vp = r.get("DD", {}).get("VP", [])
                if ua and len(vp) > 0:
                    gen_tuple = (str(ua), str(vp[0]))
                    if gen_tuple not in existing_ids:
                        new_wonders.append({
                            "GenerationID": [str(ua), str(vp[0])],
                            "WonderStatValue": 0.0,
                            "SeenInFrontend": False
                        })
                        existing_ids.add(gen_tuple)

            # Wiping Logic
            remove = False
            if not is_whitelisted:
                if wipe_hidden and is_hidden:
                    remove = True
                elif wipe_all and is_foreign:
                    remove = True
                elif is_foreign:
                    if wipe_fauna and dt == "Animal": remove = True
                    if wipe_flora and dt == "Flora": remove = True
                    if wipe_mineral and dt == "Mineral": remove = True
            else:
                if is_foreign and (wipe_all or wipe_fauna or wipe_flora or wipe_mineral or wipe_hidden):
                    whitelisted_skipped += 1

            if remove:
                removed_count += 1
            else:
                cleaned_records.append(r)

        changes_made = False
        if removed_count > 0:
            data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"] = cleaned_records
            
            # Update the memory allocation counters (v1.1.1 fix)
            new_record_count = len(cleaned_records)
            data["DiscoveryManagerData"]["DiscoveryData-v1"]["ReserveStore"] = new_record_count
            data["DiscoveryManagerData"]["DiscoveryData-v1"]["ReserveManaged"] = new_record_count
            
            changes_made = True
            log_message(log_widget, f"Successfully wiped {removed_count} unwanted records.")
            log_message(log_widget, f"Updated memory counters (ReserveStore/Managed set to {new_record_count}).")

        if whitelisted_skipped > 0:
            log_message(log_widget, f"Protected {whitelisted_skipped} records matching your whitelist.")
        
        if inject_paradise and new_wonders:
            ps["WonderPlanetRecords"] = existing_wonders + new_wonders
            changes_made = True
            log_message(log_widget, f"Injected {len(new_wonders)} planets for Paradise Quotient calculation.")

        if changes_made:
            output_path = os.path.join(os.path.dirname(filepath), "optimized_save.json")
            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(data, out, separators=(',', ':'))
            
            log_message(log_widget, f"Saved optimized save to: {output_path}")
            log_message(log_widget, "--- Optimization Complete Successfully! ---")
            messagebox.showinfo("Success", f"Optimization complete!\nBackup created at:\n{backup_filename}")
        else:
            log_message(log_widget, "No matching records found to wipe and no new planets to inject.")
            messagebox.showinfo("Done", "No matching records found. Your save is clean!")

    except Exception as e:
        log_message(log_widget, f"ERROR: {str(e)}")
        messagebox.showerror("Error", f"Failed to process file:\n{str(e)}")

# --- Modern Dark Theme UI Setup ---
root = tk.Tk()
root.title("NMS Save Optimizer v1.1.2 (Dark Edition)")
root.geometry("520x680")
root.resizable(False, False)

# Dark color palette configuration
BG_DARK = "#1e1e1e"
FG_LIGHT = "#d4d4d4"
ACCENT_COLOR = "#007acc"
FIELD_BG = "#2d2d2d"

root.configure(bg=BG_DARK)

style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background=BG_DARK)
style.configure("TLabel", background=BG_DARK, foreground=FG_LIGHT, font=("Segoe UI", 10))
style.configure("TCheckbutton", background=BG_DARK, foreground=FG_LIGHT, font=("Segoe UI", 9))
style.configure("TButton", background=ACCENT_COLOR, foreground="#ffffff", font=("Segoe UI", 10, "bold"))
style.map("TButton", background=[("active", "#005999")])

main_frame = ttk.Frame(root, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

# File Selection
ttk.Label(main_frame, text="Select Exported JSON File:").pack(anchor="w", pady=(0, 2))
file_frame = ttk.Frame(main_frame)
file_frame.pack(fill=tk.X, pady=(0, 10))
file_entry = ttk.Entry(file_frame, font=("Segoe UI", 9))
file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
ttk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.RIGHT)

# Username Input
ttk.Label(main_frame, text="Your Exact In-Game Username:").pack(anchor="w", pady=(0, 2))
user_entry = ttk.Entry(main_frame, font=("Segoe UI", 9))
user_entry.pack(fill=tk.X, pady=(0, 10))

# Whitelist Input
ttk.Label(main_frame, text="Protected Whitelist (Comma-separated names/users):").pack(anchor="w", pady=(0, 2))
whitelist_entry = ttk.Entry(main_frame, font=("Segoe UI", 9))
whitelist_entry.pack(fill=tk.X, pady=(0, 15))

# Wiping Options
ttk.Label(main_frame, text="1. Cleanup Options (Foreign Data Only):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))

var_hidden = tk.BooleanVar(value=True)
ttk.Checkbutton(main_frame, text="Wipe Hidden Systems", variable=var_hidden).pack(anchor="w", pady=1)

var_fauna = tk.BooleanVar(value=False)
ttk.Checkbutton(main_frame, text="Wipe Foreign Fauna (Animals)", variable=var_fauna).pack(anchor="w", pady=1)

var_flora = tk.BooleanVar(value=False)
ttk.Checkbutton(main_frame, text="Wipe Foreign Flora", variable=var_flora).pack(anchor="w", pady=1)

var_mineral = tk.BooleanVar(value=False)
ttk.Checkbutton(main_frame, text="Wipe Foreign Minerals", variable=var_mineral).pack(anchor="w", pady=1)

var_all = tk.BooleanVar(value=False)
ttk.Checkbutton(main_frame, text="Wipe ALL Foreign Data (Includes Planets/Systems)", variable=var_all).pack(anchor="w", pady=1)

# Paradise Option
ttk.Label(main_frame, text="2. Paradise Math:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 5))

var_paradise = tk.BooleanVar(value=False)
ttk.Checkbutton(main_frame, text="Inject Paradise Quotient records for your planets", variable=var_paradise).pack(anchor="w", pady=2)

# Execute Button
ttk.Button(main_frame, text="Optimize Save", command=lambda: optimize_save(log_box)).pack(fill=tk.X, pady=(15, 10))

# Detailed Summary Log Window
ttk.Label(main_frame, text="Execution Activity Log:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5, 2))
log_frame = ttk.Frame(main_frame)
log_frame.pack(fill=tk.BOTH, expand=True)

log_box = tk.Text(log_frame, height=7, bg=FIELD_BG, fg="#4ec9b0", insertbackground="white", font=("Consolas", 9), relief=tk.FLAT)
log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
log_box.config(state=tk.DISABLED)

scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_box.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_box.config(yscrollcommand=scrollbar.set)

root.mainloop()