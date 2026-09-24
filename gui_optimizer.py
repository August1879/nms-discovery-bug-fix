import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import urllib.request
import urllib.error
import webbrowser
import threading

from save_safety import load_json, optimize_data, write_output

CURRENT_VERSION = "v1.1.7"
REPO_URL = "https://api.github.com/repos/August1879/nms-discovery-bug-fix/releases/latest"

def check_for_updates():
    def _check():
        try:
            req = urllib.request.Request(REPO_URL, headers={'User-Agent': 'NMS-Optimizer'})
            with urllib.request.urlopen(req, timeout=3) as response:
                import json
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get("tag_name")
                
                if latest_version and latest_version != CURRENT_VERSION:
                    release_url = data.get("html_url")
                    
                    # Schedule the popup on the main Tkinter thread
                    root.after(0, lambda: prompt_update(latest_version, release_url))
        except Exception:
            pass # Fail silently if they have no internet connection

    def prompt_update(latest, url):
        msg = f"A new version of the Optimizer ({latest}) is available!\n\nYou are currently running {CURRENT_VERSION}.\n\nWould you like to download the update?"
        if messagebox.askyesno("Update Available", msg):
            webbrowser.open(url)

    # Run the internet check in the background
    threading.Thread(target=_check, daemon=True).start()

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

def confirm_changes(removed, added, remaining_count):
    preview = tk.Toplevel(root)
    preview.title("Review save changes")
    preview.geometry("700x480")
    preview.transient(root)
    preview.grab_set()
    approved = tk.BooleanVar(value=False)

    ttk.Label(preview, text=f"Remove {len(removed)} discoveries; add {len(added)} Paradise records.").pack(anchor="w", padx=12, pady=8)
    detail_frame = ttk.Frame(preview)
    detail_frame.pack(fill=tk.BOTH, expand=True, padx=12)
    details = tk.Text(detail_frame, wrap="word")
    details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=details.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    details.config(yscrollcommand=scrollbar.set)
    for index, record_type, name, owner in removed:
        details.insert(tk.END, f"Remove record #{index}: {record_type!r}, {name!r}, owner {owner!r}\n")
    if removed:
        details.insert(tk.END, f"Set ReserveStore and ReserveManaged to {remaining_count}.\n")
    for wonder in added:
        details.insert(tk.END, f"Add Paradise record: {wonder['GenerationID']!r}\n")
    details.config(state=tk.DISABLED)

    def accept():
        approved.set(True)
        preview.destroy()

    buttons = ttk.Frame(preview, padding=12)
    buttons.pack(fill=tk.X)
    ttk.Button(buttons, text="Cancel", command=preview.destroy).pack(side=tk.RIGHT)
    ttk.Button(buttons, text="Write reviewed changes", command=accept).pack(side=tk.RIGHT, padx=8)
    preview.protocol("WM_DELETE_WINDOW", preview.destroy)
    root.wait_window(preview)
    return approved.get()

def optimize_save(log_widget):
    filepath = file_entry.get().strip()
    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Please select a valid full_save.json file.")
        return

    # Check for Goatfungus memory crash (0-byte file) before handing it to the parser
    if os.path.getsize(filepath) == 0:
        log_message(log_widget, "ERROR: Detected 0-byte file. Save Editor memory crash suspected.")
        error_msg = (
            "The selected JSON file is completely empty (0 bytes).\n\n"
            "DIAGNOSIS:\n"
            "Your Save Editor ran out of memory while trying to export your massive legacy save file.\n\n"
            "HOW TO FIX IT:\n"
            "1. Open your Windows Command Prompt in your Goatfungus folder.\n"
            "2. Run this exact command to give it more RAM:\n"
            "java -Xmx4G -jar NMSSaveEditor.jar\n"
            "3. Export the JSON again and bring it back here."
        )
        messagebox.showerror("Export Crash Detected", error_msg)
        return

    username = user_entry.get().strip()
    if not username:
        messagebox.showerror("Error", "Please enter your in-game username.")
        return

    # Parse whitelist inputs
    whitelist_raw = whitelist_entry.get().strip()
    whitelisted_names = {w.strip() for w in whitelist_raw.split(",") if w.strip()}

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
        log_message(log_widget, "Loading save file...")
        data, original = load_json(filepath)
        options = {"hidden": wipe_hidden, "fauna": wipe_fauna, "flora": wipe_flora,
                   "mineral": wipe_mineral, "all": wipe_all, "paradise": inject_paradise}
        removed, added, protected = optimize_data(data, username, whitelisted_names, options)

        if protected:
            log_message(log_widget, f"Protected {protected} records matching your whitelist.")
        if not removed and not added:
            log_message(log_widget, "No matching records found to change.")
            messagebox.showinfo("Done", "No matching records found. No output was written.")
            return

        remaining_count = len(data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"])
        if not confirm_changes(removed, added, remaining_count):
            log_message(log_widget, "Cancelled before writing any files.")
            return

        backup_path, output_path = write_output(filepath, data, original, "optimized_save.json")
        log_message(log_widget, f"Removed {len(removed)} records; added {len(added)} Paradise records.")
        log_message(log_widget, f"Saved original backup to: {backup_path}")
        log_message(log_widget, f"Saved optimized save to: {output_path}")
        
        # Inject NomNom Warning into success message
        success_msg = (
            f"Optimization complete!\n"
            f"Original backup: {backup_path.name}\n"
            f"Output: {output_path.name}\n\n"
            "CRITICAL WARNING FOR LEGACY PLAYERS:\n"
            "If your save is from the Atlas Rises era, DO NOT use NomNom to import this new file. "
            "NomNom has a known bug that will permanently turn your legacy ships into default fighters.\n\n"
            "Use Goatfungus to import this optimized file to keep your ships safe."
        )
        messagebox.showinfo("Success - Read Carefully", success_msg)

    except Exception as e:
        log_message(log_widget, f"ERROR: {str(e)}")
        messagebox.showerror("Error", f"Failed to process file:\n{str(e)}")


# --- Modern Dark Theme UI Setup ---
root = tk.Tk()
root.title(f"NMS Save Optimizer {CURRENT_VERSION} (Dark Edition)")
root.geometry("520x720") # Slightly increased height to accommodate the ad
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
ttk.Label(main_frame, text="Protected Record Names or Users (comma-separated):").pack(anchor="w", pady=(0, 2))
whitelist_entry = ttk.Entry(main_frame, font=("Segoe UI", 9))
whitelist_entry.pack(fill=tk.X, pady=(0, 15))

# Wiping Options
ttk.Label(main_frame, text="1. Cleanup Options:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))

var_hidden = tk.BooleanVar(value=False)
ttk.Checkbutton(main_frame, text="Wipe Hidden Systems (including yours)", variable=var_hidden).pack(anchor="w", pady=1)

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

# --- Alliance Advertisement Section ---
ad_frame = tk.Frame(main_frame, bg=BG_DARK)
ad_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

ad_title = tk.Label(ad_frame, text="🌌 Found a pristine Earth-like planet! Join the Alliance:", bg=BG_DARK, fg=FG_LIGHT, font=("Segoe UI", 9))
ad_title.pack()

links_frame = tk.Frame(ad_frame, bg=BG_DARK)
links_frame.pack(pady=2)

reddit_link = tk.Label(links_frame, text="[View Reddit Post]", fg="#ff4500", bg=BG_DARK, cursor="hand2", font=("Segoe UI", 9, "bold"))
reddit_link.pack(side=tk.LEFT, padx=10)
reddit_link.bind("<Button-1>", lambda e: webbrowser.open("https://www.reddit.com/r/NoMansSkyTheGame/s/LTUupn3YrA"))

discord_link = tk.Label(links_frame, text="[Add on Discord]", fg="#5865F2", bg=BG_DARK, cursor="hand2", font=("Segoe UI", 9, "bold"))
discord_link.pack(side=tk.LEFT, padx=10)
discord_link.bind("<Button-1>", lambda e: webbrowser.open("https://discord.com/users/1082971394968657920"))

# Check for updates in the background before starting the main loop
check_for_updates()

root.mainloop()