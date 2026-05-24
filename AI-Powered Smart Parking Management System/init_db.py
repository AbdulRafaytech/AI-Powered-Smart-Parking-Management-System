import sqlite3
from database import get_db_connection

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            slot_id INTEGER,
            entry_time TIMESTAMP
        )
    ''')

    # Parking Slots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_slots (
            slot_id INTEGER PRIMARY KEY,
            slot_type TEXT NOT NULL,
            is_occupied BOOLEAN DEFAULT FALSE
        )
    ''')

    # Receipts/Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            amount REAL,
            payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')

    # Blacklist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            plate_number TEXT PRIMARY KEY,
            reason TEXT
        )
    ''')

    # Parking History
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT,
            entry_time TIMESTAMP,
            exit_time TIMESTAMP,
            slot_id INTEGER
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM parking_slots")
    if cursor.fetchone()[0] == 0:
        slots = [
            (1, 'Normal'), (2, 'Normal'), (3, 'Normal'),
            (4, 'Disabled'), (5, 'VIP'), (6, 'Bike'),
            (7, 'Normal'), (8, 'Normal'), (9, 'Normal'), (10, 'Normal')
        ]
        cursor.executemany("INSERT INTO parking_slots (slot_id, slot_type) VALUES (?, ?)", slots)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
