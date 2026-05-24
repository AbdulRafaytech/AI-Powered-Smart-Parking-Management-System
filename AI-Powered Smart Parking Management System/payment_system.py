from database import get_db_connection

def add_payment(vehicle_id, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO receipts (vehicle_id, amount) VALUES (?, ?)"
    cursor.execute(query, (vehicle_id, amount))
    conn.commit()
    conn.close()

def calculate_fee(hours_parked):
    rate_per_hour = 50  # PKR
    return hours_parked * rate_per_hour
