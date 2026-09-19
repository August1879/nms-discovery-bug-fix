import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filepath)

def optimize_save():
    filepath = file_entry.get().strip()
    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Please select a valid full_save.json file.")
        return

    username = user_entry.get().strip()
    if not username:
        messagebox.showerror("Error", "Please enter your in-game username.")
        return

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
        # Read and sanitize JSON
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        content = content.replace('\\', '\\\\').replace('\\\\"', '\\"')
        content = "".join(ch for ch in content if ord(ch) >= 32 or ch in '\n\r\t')
        data = json.loads(content, strict=False)

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
        new_wonders = []

        for r in records:
            dt = r.get("DD", {}).get("DT", "")
            usn = r.get("OWS", {}).get("USN", "")
            
            is_hidden = r.get("FL", {}).get("F") == 1
            is_foreign = (usn != username and usn != "")
            is_mine = (usn == username)

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
            if wipe_hidden and is_hidden:
                remove = True
            elif wipe_all and is_foreign:
                remove = True
            elif is_foreign:
                if wipe_fauna and dt == "Animal": remove = True
                if wipe_flora and dt == "Flora": remove = True
                if wipe_mineral and dt == "Mineral": remove = True

            if remove:
                removed_count += 1
            else:
                cleaned_records.append(r)

        # Apply modifications if changes were made
        changes_made = False
        message_parts = []

        if removed_count > 0:
            data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"] = cleaned_records
            changes_made = True
            message_parts.append(f"Wiped {removed_count} unwanted records.")
        
        if inject_paradise and new_wonders:
            ps["WonderPlanetRecords"] = existing_wonders + new_wonders
            changes_made = True
            message_parts.append(f"Injected {len(new_wonders)} planets for Paradise Quotient calculation.")

        if changes_made:
            output_path = os.path.join(os.path.dirname(filepath), "optimized_save.json")
            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(data, out, separators=(',', ':'))
            
            final_msg = "\n".join(message_parts) + f"\n\nSaved to: {output_path}"
            messagebox.showinfo("Success", final_msg)
        else:
            messagebox.showinfo("Done", "No matching records found to wipe and no new planets to inject.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{str(e)}")

# --- UI Setup ---
root = tk.Tk()
root.title("NMS Save Optimizer v1.1")
root.geometry("450x520")
root.resizable(False, False)

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

# File Selection
ttk.Label(frame, text="Select Exported JSON File:").pack(anchor="w")
file_frame = ttk.Frame(frame)
file_frame.pack(fill=tk.X, pady=(0, 15))
file_entry = ttk.Entry(file_frame)
file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
ttk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.RIGHT)

# Username Input (Left blank so users must enter their own)
ttk.Label(frame, text="Your Exact In-Game Username:").pack(anchor="w")
user_entry = ttk.Entry(frame)
user_entry.pack(fill=tk.X, pady=(0, 15))

# Wiping Options
ttk.Label(frame, text="1. Cleanup Options (Foreign Data Only):", font=("", 10, "bold")).pack(anchor="w", pady=(0, 5))

var_hidden = tk.BooleanVar(value=True)
ttk.Checkbutton(frame, text="Wipe Hidden Systems (You pressed 'F' to hide)", variable=var_hidden).pack(anchor="w", pady=2)

var_fauna = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Wipe Foreign Fauna (Animals)", variable=var_fauna).pack(anchor="w", pady=2)

var_flora = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Wipe Foreign Flora", variable=var_flora).pack(anchor="w", pady=2)

var_mineral = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Wipe Foreign Minerals", variable=var_mineral).pack(anchor="w", pady=2)

var_all = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Wipe ALL Foreign Data (Includes Planets/Systems)", variable=var_all).pack(anchor="w", pady=2)

# Paradise Option
ttk.Label(frame, text="2. Paradise Math:", font=("", 10, "bold")).pack(anchor="w", pady=(15, 5))

var_paradise = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Inject Paradise Quotient records for your planets", variable=var_paradise).pack(anchor="w", pady=2)

# Execute Button
ttk.Button(frame, text="Optimize Save", command=optimize_save).pack(fill=tk.X, pady=(20, 0))

root.mainloop()