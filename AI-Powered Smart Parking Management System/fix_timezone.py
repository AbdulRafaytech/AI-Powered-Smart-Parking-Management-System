import os
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Define the replacement for datetime.datetime.now()
    # We use a helper function or a direct timedelta since pytz is missing

    # 1. Ensure 'datetime' is imported
    if 'import datetime' not in content:
        content = 'import datetime\n' + content

    # 2. Replace datetime.datetime.now()
    # We want datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)))
    content = content.replace('datetime.datetime.now()', 'datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)))')

    # 3. Handle cases where they might use datetime.datetime.now().strftime(...)
    # The replacement above handles the .now() part, but we should make sure it works.

    # 4. Specifically for SQLite CURRENT_TIMESTAMP which is UTC
    # If the user is using DEFAULT CURRENT_TIMESTAMP, it will be UTC.
    # We should probably change those to manual inserts or adjust how we read them.

    with open(filepath, 'w') as f:
        f.write(content)

files_to_fix = ['app.py', 'vehicle.py', 'ai_logic.py', 'generate_dummy_data.py']
for f in files_to_fix:
    if os.path.exists(f):
        fix_file(f)
        print(f"Fixed {f}")
