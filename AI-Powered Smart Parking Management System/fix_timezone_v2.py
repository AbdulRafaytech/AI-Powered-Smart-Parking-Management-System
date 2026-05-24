import os

def fix_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r') as f:
        content = f.read()

    # Use naive datetime with 5 hour offset to avoid subtraction errors
    # datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).replace(tzinfo=None)

    pattern = 'datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)))'
    replacement = 'datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).replace(tzinfo=None)'

    content = content.replace(pattern, replacement)

    with open(filepath, 'w') as f:
        f.write(content)

files_to_fix = ['app.py', 'vehicle.py', 'ai_logic.py', 'generate_dummy_data.py']
for f in files_to_fix:
    fix_file(f)
    print(f"Refixed {f}")
