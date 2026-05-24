from database import get_db_connection
from vehicle import add_vehicle, remove_vehicle
from parking_slot import occupy_slot, free_slot, get_available_slots
from payment_system import add_payment, calculate_fee

def park_vehicle(vehicle_number, vehicle_type, slot_number):
    available_slots = get_available_slots()
    slot = next((s for s in available_slots if s[0] == int(slot_number)), None)
    if slot:
        vehicle_id = add_vehicle(vehicle_number, vehicle_type, slot_number)
        occupy_slot(slot[0])
        print(f"Vehicle parked in slot {slot_number}.")
        return vehicle_id
    else:
        print("No available slot with this number!")
        return None

def remove_parked_vehicle(vehicle_id, hours_parked):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT slot_id FROM vehicles WHERE id=?", (vehicle_id,))
    res = cursor.fetchone()
    slot_id = res[0] if res else None
    conn.close()

    fee = calculate_fee(hours_parked)
    add_payment(vehicle_id, fee)

    if slot_id:
        free_slot(slot_id)

    remove_vehicle(vehicle_id)
    print(f"Vehicle {vehicle_id} removed. Fee: {fee}")
