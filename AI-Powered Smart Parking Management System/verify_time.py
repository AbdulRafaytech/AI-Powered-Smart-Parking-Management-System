import sqlite3
import datetime

conn = sqlite3.connect('parking_system.db')
cursor = conn.cursor()

# Check dummy data times
cursor.execute("SELECT entry_time FROM parking_history LIMIT 1")
row = cursor.fetchone()
print(f"Sample History Entry Time: {row[0]}")

# Check current time logic
now_pk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).replace(tzinfo=None)
print(f"Calculated PK Time: {now_pk}")

conn.close()
