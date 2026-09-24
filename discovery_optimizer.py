from save_safety import load_json, optimize_data, write_output


print("\n--- NMS Discovery Cache Optimizer ---")
print("1: Wipe hidden systems (including yours)")
print("2: Wipe foreign flora, fauna, and minerals")
print("3: Wipe all foreign discoveries")
print("4: Cancel and exit")
choice = input("\nEnter choice (1-4): ").strip()
if choice not in ("1", "2", "3"):
    print("Exiting.")
    raise SystemExit(0)

username = input("Enter your in-game username: ").strip()
if not username:
    raise SystemExit("A username is required.")

data, original = load_json("full_save.json")
options = {"hidden": choice == "1", "fauna": choice == "2", "flora": choice == "2",
           "mineral": choice == "2", "all": choice == "3", "paradise": False}
removed, _, _ = optimize_data(data, username, set(), options, update_reserves=False)
if not removed:
    raise SystemExit("No matching records found. No output was written.")

print(f"Review {len(removed)} records to remove:")
for index, record_type, name, owner in removed:
    print(f"  #{index}: {record_type!r}, {name!r}, owner {owner!r}")
if input("Type DELETE to write the result: ").strip() != "DELETE":
    print("Cancelled before writing any files.")
    raise SystemExit(0)

backup, output = write_output("full_save.json", data, original, "optimized_save.json")
print(f"Original backup: {backup}\nOptimized output: {output}")
