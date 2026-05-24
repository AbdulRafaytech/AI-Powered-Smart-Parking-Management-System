import sqlite3
import datetime
import random

def generate_data():
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    # Generate 100 history records
    plates = ["ABC-123", "XYZ-789", "LHR-555", "KHI-999", "ISB-001", "RWP-444"]

    # Peak hours usually around 9 AM and 6 PM
    peak_hours = [8, 9, 10, 17, 18, 19]
    other_hours = [11, 12, 13, 14, 15, 16, 20, 21, 22]

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).replace(tzinfo=None)

    for i in range(100):
        if random.random() < 0.7:
            hour = random.choice(peak_hours)
        else:
            hour = random.choice(other_hours)

        day_offset = random.randint(1, 30)
        entry_time = now - datetime.timedelta(days=day_offset)
        entry_time = entry_time.replace(hour=hour, minute=random.randint(0, 59))

        stay_duration = random.randint(1, 8)
        exit_time = entry_time + datetime.timedelta(hours=stay_duration)

        cursor.execute('''
            INSERT INTO parking_history (plate_number, entry_time, exit_time, slot_id)
            VALUES (?, ?, ?, ?)
        ''', (random.choice(plates), entry_time.strftime('%Y-%m-%d %H:%M:%S'),
              exit_time.strftime('%Y-%m-%d %H:%M:%S'), random.randint(1, 10)))

    # Add some blacklisted vehicles
    cursor.execute("INSERT OR IGNORE INTO blacklist (plate_number, reason) VALUES (?, ?)", ("STOLEN-1", "Reported Stolen"))
    cursor.execute("INSERT OR IGNORE INTO blacklist (plate_number, reason) VALUES (?, ?)", ("FINE-404", "Pending Fines > 5000"))

    conn.commit()
    conn.close()
    print("Dummy data generated.")

if __name__ == "__main__":
    generate_data()
