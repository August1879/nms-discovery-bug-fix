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
        username = "augustdheart0"

    wipe_hidden = var_hidden.get()
    wipe_ffm = var_ffm.get()
    wipe_all = var_all.get()

    if not any([wipe_hidden, wipe_ffm, wipe_all]):
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
        
        cleaned_records = []
        removed_count = 0

        for r in records:
            dt = r.get("DD", {}).get("DT", "")
            usn = r.get("OWS", {}).get("USN", "")
            
            is_hidden = r.get("FL", {}).get("F") == 1
            is_foreign = (usn != username and usn != "")

            remove = False
            if wipe_hidden and is_hidden:
                remove = True
            elif wipe_all and is_foreign:
                remove = True
            elif wipe_ffm and dt in ["Animal", "Flora", "Mineral"] and is_foreign:
                remove = True

            if remove:
                removed_count += 1
            else:
                cleaned_records.append(r)

        if removed_count > 0:
            data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"] = cleaned_records
            output_path = os.path.join(os.path.dirname(filepath), "optimized_save.json")
            
            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(data, out, separators=(',', ':'))
            
            messagebox.showinfo("Success", f"Wiped {removed_count} records!\n\nSaved to: {output_path}")
        else:
            messagebox.showinfo("Done", "No matching records found. Your save is clean!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{str(e)}")

# --- UI Setup ---
root = tk.Tk()
root.title("No Man's Sky Discovery Optimizer")
root.geometry("450x380")
root.resizable(False, False)

# Padding and styling
frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

# File Selection
ttk.Label(frame, text="Select Exported JSON File:").pack(anchor="w")
file_frame = ttk.Frame(frame)
file_frame.pack(fill=tk.X, pady=(0, 15))
file_entry = ttk.Entry(file_frame)
file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
ttk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.RIGHT)

# Username Input
ttk.Label(frame, text="Your Exact In-Game Username:").pack(anchor="w")
user_entry = ttk.Entry(frame)
user_entry.insert(0, "augustdheart0")
user_entry.pack(fill=tk.X, pady=(0, 20))

# Options
ttk.Label(frame, text="Select Data to Wipe:", font=("", 10, "bold")).pack(anchor="w", pady=(0, 5))

var_hidden = tk.BooleanVar(value=True)
ttk.Checkbutton(frame, text="Hidden Systems (You pressed 'F' to hide)", variable=var_hidden).pack(anchor="w", pady=2)

var_ffm = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Foreign Flora, Fauna, and Minerals only", variable=var_ffm).pack(anchor="w", pady=2)

var_all = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="ALL Foreign Discoveries (Includes planets)", variable=var_all).pack(anchor="w", pady=2)

# Execute Button
ttk.Button(frame, text="Optimize Save", command=optimize_save, style="Accent.TButton").pack(fill=tk.X, pady=(25, 0))

root.mainloop()