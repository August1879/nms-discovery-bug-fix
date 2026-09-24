from save_safety import load_json, optimize_data, write_output


username = input("Enter your in-game username: ").strip()
if not username:
    raise SystemExit("A username is required.")

data, original = load_json("full_save.json")
options = {"hidden": False, "fauna": False, "flora": False,
           "mineral": False, "all": False, "paradise": True}
_, added, _ = optimize_data(data, username, set(), options)
if not added:
    raise SystemExit("No new planets to add. No output was written.")

print(f"Review {len(added)} Paradise records to add:")
for wonder in added:
    print(f"  {wonder['GenerationID']!r}")
if input("Type ADD to write the result: ").strip() != "ADD":
    print("Cancelled before writing any files.")
    raise SystemExit(0)

backup, output = write_output("full_save.json", data, original, "new_save.json")
print(f"Original backup: {backup}\nOptimized output: {output}")
