from database import get_db_connection

def add_slot(slot_id, slot_type='Normal'):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO parking_slots (slot_id, slot_type) VALUES (?, ?)"
    cursor.execute(query, (slot_id, slot_type))
    conn.commit()
    conn.close()

def occupy_slot(slot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE parking_slots SET is_occupied=TRUE WHERE slot_id=?"
    cursor.execute(query, (slot_id,))
    conn.commit()
    conn.close()

def free_slot(slot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE parking_slots SET is_occupied=FALSE WHERE slot_id=?"
    cursor.execute(query, (slot_id,))
    conn.commit()
    conn.close()

def get_available_slots():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT slot_id, slot_type FROM parking_slots WHERE is_occupied=FALSE")
    slots = cursor.fetchall()
    conn.close()
    return slots
