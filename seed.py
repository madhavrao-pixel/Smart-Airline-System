"""
Seed script for Apex Voyage database.
Generates flights for every day from 2026-05-11 to 2026-07-30.
"""
from app import app, db
from models import Flight
from datetime import date, timedelta
import random

random.seed(42)

def add_minutes(time_str, minutes):
    h, m = map(int, time_str.split(':'))
    total = h * 60 + m + minutes
    total %= 1440
    return f"{total // 60:02d}:{total % 60:02d}"

# (flight_number, origin_code, origin_city, dest_code, dest_city,
#  dep_time, duration_mins, aircraft, eco_range, biz_range, first_range, eco_seats, biz_seats, first_seats)
DOMESTIC_ROUTES = [
    ('AV101', 'BOM', 'Mumbai',    'DEL', 'Delhi',     '06:00', 110, 'Airbus A320neo',     (3500,7500),  (22000,42000),  (95000,120000), 180, 36, 12),
    ('AV102', 'DEL', 'Delhi',     'BOM', 'Mumbai',    '09:30', 110, 'Airbus A320neo',     (3500,7500),  (22000,42000),  (95000,120000), 180, 36, 12),
    ('AV103', 'BOM', 'Mumbai',    'BLR', 'Bangalore', '07:30', 105, 'Boeing 787 Dreamliner',(3800,8000),(24000,44000),  (98000,125000), 200, 40, 14),
    ('AV104', 'BLR', 'Bangalore', 'BOM', 'Mumbai',    '11:00', 105, 'Airbus A320neo',     (3800,8000),  (24000,44000),  (98000,125000), 180, 36, 12),
    ('AV105', 'DEL', 'Delhi',     'MAA', 'Chennai',   '08:00', 150, 'Airbus A320neo',     (4200,8500),  (26000,46000),  (99000,130000), 180, 36, 12),
    ('AV106', 'MAA', 'Chennai',   'DEL', 'Delhi',     '14:00', 150, 'Airbus A320neo',     (4200,8500),  (26000,46000),  (99000,130000), 180, 36, 12),
    ('AV107', 'DEL', 'Delhi',     'CCU', 'Kolkata',   '10:00', 135, 'Airbus A320neo',     (3600,7800),  (23000,43000),  (96000,122000), 180, 36, 12),
    ('AV108', 'CCU', 'Kolkata',   'DEL', 'Delhi',     '16:30', 135, 'Airbus A320neo',     (3600,7800),  (23000,43000),  (96000,122000), 180, 36, 12),
    ('AV109', 'BLR', 'Bangalore', 'HYD', 'Hyderabad', '09:30', 75,  'Airbus A320neo',    (3500,6500),  (20000,38000),  (93000,115000), 180, 30, 10),
    ('AV110', 'HYD', 'Hyderabad', 'BLR', 'Bangalore', '12:00', 75,  'Airbus A320neo',    (3500,6500),  (20000,38000),  (93000,115000), 180, 30, 10),
    ('AV111', 'BOM', 'Mumbai',    'GOI', 'Goa',       '07:00', 70,  'Airbus A320neo',    (3500,6000),  (20000,35000),  (92000,110000), 180, 30, 10),
    ('AV112', 'GOI', 'Goa',       'BOM', 'Mumbai',    '15:30', 70,  'Airbus A320neo',    (3500,6000),  (20000,35000),  (92000,110000), 180, 30, 10),
    ('AV113', 'DEL', 'Delhi',     'JAI', 'Jaipur',    '08:30', 65,  'Airbus A320neo',    (3500,5500),  (19000,32000),  (90000,108000), 150, 24,  8),
    ('AV114', 'JAI', 'Jaipur',    'DEL', 'Delhi',     '11:00', 65,  'Airbus A320neo',    (3500,5500),  (19000,32000),  (90000,108000), 150, 24,  8),
    ('AV115', 'MAA', 'Chennai',   'CCU', 'Kolkata',   '07:30', 105, 'Airbus A320neo',    (3800,7500),  (22000,40000),  (94000,118000), 180, 36, 12),
    ('AV116', 'CCU', 'Kolkata',   'MAA', 'Chennai',   '13:00', 105, 'Airbus A320neo',    (3800,7500),  (22000,40000),  (94000,118000), 180, 36, 12),
    ('AV117', 'BOM', 'Mumbai',    'DEL', 'Delhi',     '14:00', 115, 'Airbus A380',        (4500,9000),  (28000,48000), (105000,135000), 400, 60, 16),
    ('AV118', 'DEL', 'Delhi',     'BOM', 'Mumbai',    '19:00', 115, 'Airbus A380',        (4500,9000),  (28000,48000), (105000,135000), 400, 60, 16),
]

INTERNATIONAL_ROUTES = [
    ('AV201', 'BOM', 'Mumbai',    'DXB', 'Dubai',        '02:00', 210, 'Airbus A380',         (8500,16000),  (45000,80000), (130000,200000), 400, 60, 16),
    ('AV202', 'DXB', 'Dubai',     'BOM', 'Mumbai',       '10:00', 210, 'Airbus A380',         (8500,16000),  (45000,80000), (130000,200000), 400, 60, 16),
    ('AV203', 'DEL', 'Delhi',     'SIN', 'Singapore',    '23:30', 330, 'Boeing 787 Dreamliner',(10000,18000),(55000,85000), (150000,220000), 250, 48, 14),
    ('AV204', 'SIN', 'Singapore', 'DEL', 'Delhi',        '08:00', 330, 'Boeing 787 Dreamliner',(10000,18000),(55000,85000), (150000,220000), 250, 48, 14),
    ('AV205', 'BOM', 'Mumbai',    'BKK', 'Bangkok',      '01:00', 255, 'Boeing 787 Dreamliner',(9000,17000), (50000,82000), (145000,215000), 250, 48, 14),
    ('AV206', 'BKK', 'Bangkok',   'BOM', 'Mumbai',       '09:30', 255, 'Boeing 787 Dreamliner',(9000,17000), (50000,82000), (145000,215000), 250, 48, 14),
    ('AV207', 'DEL', 'Delhi',     'KUL', 'Kuala Lumpur', '22:00', 345, 'Airbus A380',         (10500,17500),(52000,83000), (148000,218000), 400, 60, 16),
    ('AV208', 'KUL', 'Kuala Lumpur','DEL','Delhi',       '10:30', 345, 'Airbus A380',         (10500,17500),(52000,83000), (148000,218000), 400, 60, 16),
    ('AV209', 'MAA', 'Chennai',   'SIN', 'Singapore',    '08:00', 240, 'Boeing 787 Dreamliner',(9500,16500), (48000,78000), (140000,210000), 250, 48, 14),
    ('AV210', 'SIN', 'Singapore', 'MAA', 'Chennai',      '16:00', 240, 'Boeing 787 Dreamliner',(9500,16500), (48000,78000), (140000,210000), 250, 48, 14),
    ('AV211', 'BOM', 'Mumbai',    'NRT', 'Tokyo',        '00:30', 510, 'Airbus A380',         (13000,18000),(65000,85000), (170000,220000), 400, 60, 16),
    ('AV212', 'NRT', 'Tokyo',     'BOM', 'Mumbai',       '14:00', 510, 'Airbus A380',         (13000,18000),(65000,85000), (170000,220000), 400, 60, 16),
    ('AV213', 'DEL', 'Delhi',     'HKG', 'Hong Kong',    '21:00', 315, 'Boeing 777X',         (11000,17800),(58000,84000), (155000,218000), 350, 52, 14),
    ('AV214', 'HKG', 'Hong Kong', 'DEL', 'Delhi',        '07:30', 315, 'Boeing 777X',         (11000,17800),(58000,84000), (155000,218000), 350, 52, 14),
    ('AV215', 'BLR', 'Bangalore', 'SIN', 'Singapore',    '10:00', 260, 'Boeing 787 Dreamliner',(10000,17000),(50000,80000), (142000,212000), 250, 48, 14),
    ('AV216', 'SIN', 'Singapore', 'BLR', 'Bangalore',    '18:00', 260, 'Boeing 787 Dreamliner',(10000,17000),(50000,80000), (142000,212000), 250, 48, 14),
    ('AV217', 'BOM', 'Mumbai',    'CMB', 'Colombo',      '06:30', 120, 'Airbus A320neo',      (7500,13000), (38000,68000), (120000,180000), 180, 36, 12),
    ('AV218', 'CMB', 'Colombo',   'BOM', 'Mumbai',       '10:30', 120, 'Airbus A320neo',      (7500,13000), (38000,68000), (120000,180000), 180, 36, 12),
    ('AV219', 'DEL', 'Delhi',     'KTM', 'Kathmandu',    '07:00', 105, 'Airbus A320neo',      (6500,12000), (32000,60000), (110000,165000), 180, 30, 10),
    ('AV220', 'KTM', 'Kathmandu', 'DEL', 'Delhi',        '10:30', 105, 'Airbus A320neo',      (6500,12000), (32000,60000), (110000,165000), 180, 30, 10),
]

ALL_ROUTES = DOMESTIC_ROUTES + INTERNATIONAL_ROUTES

def run_seed():
    with app.app_context():
        if Flight.query.count() > 0:
            print(f"Database already has {Flight.query.count()} flights. Skipping seed.")
            print("To reseed, delete instance/apex.db and run again.")
            return

        db.create_all()

        start = date(2026, 5, 11)
        end   = date(2026, 7, 30)
        delta = (end - start).days + 1

        flights_added = 0
        for day_offset in range(delta):
            current_date = start + timedelta(days=day_offset)
            random.seed(day_offset * 137 + 42)

            for route in ALL_ROUTES:
                (fn, orig_c, orig_city, dest_c, dest_city,
                 dep_time, dur_mins, aircraft,
                 eco_r, biz_r, first_r,
                 eco_s, biz_s, first_s) = route

                # Add small price variation per day (±8%)
                eco_price   = round(random.uniform(*eco_r)   * random.uniform(0.92, 1.08))
                biz_price   = round(random.uniform(*biz_r)   * random.uniform(0.92, 1.08))
                first_price = round(random.uniform(*first_r) * random.uniform(0.92, 1.08))

                arr_time = add_minutes(dep_time, dur_mins)

                f = Flight(
                    flight_number    = fn,
                    origin_code      = orig_c,
                    origin_city      = orig_city,
                    destination_code = dest_c,
                    destination_city = dest_city,
                    departure_time   = dep_time,
                    arrival_time     = arr_time,
                    date             = current_date,
                    aircraft_type    = aircraft,
                    economy_price    = eco_price,
                    business_price   = biz_price,
                    first_price      = first_price,
                    economy_seats    = eco_s,
                    business_seats   = biz_s,
                    first_seats      = first_s,
                    status           = 'Scheduled',
                )
                db.session.add(f)
                flights_added += 1

            if day_offset % 20 == 0:
                db.session.flush()
                print(f"  Generating: {current_date} ({flights_added} flights so far)...")

        db.session.commit()
        print(f"\nDone! Seeded {flights_added} flights across {delta} days.")
        print(f"Date range: {start} to {end}")
        print(f"Routes: {len(DOMESTIC_ROUTES)} domestic + {len(INTERNATIONAL_ROUTES)} international")

if __name__ == '__main__':
    run_seed()
