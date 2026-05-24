from database import get_db_connection

def add_vehicle(plate_number, vehicle_type, slot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    import datetime
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
    query = "INSERT INTO vehicles (plate_number, vehicle_type, slot_id, entry_time) VALUES (?, ?, ?, ?)"
    cursor.execute(query, (plate_number, vehicle_type, slot_id, now))
    conn.commit()
    vehicle_id = cursor.lastrowid
    conn.close()
    return vehicle_id

def remove_vehicle(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT plate_number, entry_time, slot_id FROM vehicles WHERE id=?", (vehicle_id,))
    v = cursor.fetchone()
    if v:
        import datetime
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO parking_history (plate_number, entry_time, exit_time, slot_id) VALUES (?, ?, ?, ?)",
                       (v[0], v[1], now, v[2]))

    query = "DELETE FROM vehicles WHERE id=?"
    cursor.execute(query, (vehicle_id,))
    conn.commit()
    conn.close()

def get_all_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    conn.close()
    return vehicles
