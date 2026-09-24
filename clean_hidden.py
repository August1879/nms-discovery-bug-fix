from save_safety import load_json, optimize_data, write_output


username = input("Enter your in-game username: ").strip()
if not username:
    raise SystemExit("A username is required.")

data, original = load_json("full_save.json")
options = {"hidden": True, "fauna": False, "flora": False,
           "mineral": False, "all": False, "paradise": False}
removed, _, _ = optimize_data(data, username, set(), options, update_reserves=False)
if not removed:
    raise SystemExit("No hidden systems found. No output was written.")

print(f"Review {len(removed)} hidden systems to remove (including your own):")
for index, record_type, name, owner in removed:
    print(f"  #{index}: {record_type!r}, {name!r}, owner {owner!r}")
if input("Type DELETE to write the result: ").strip() != "DELETE":
    print("Cancelled before writing any files.")
    raise SystemExit(0)

backup, output = write_output("full_save.json", data, original, "clean_save.json")
print(f"Original backup: {backup}\nOptimized output: {output}")
