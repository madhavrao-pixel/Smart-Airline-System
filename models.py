from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()


class Flight(db.Model):
    __tablename__ = 'flights'
    id               = db.Column(db.Integer, primary_key=True)
    flight_number    = db.Column(db.String(10), nullable=False)
    origin_code      = db.Column(db.String(5), nullable=False)
    origin_city      = db.Column(db.String(100), nullable=False)
    destination_code = db.Column(db.String(5), nullable=False)
    destination_city = db.Column(db.String(100), nullable=False)
    departure_time   = db.Column(db.String(10), nullable=False)
    arrival_time     = db.Column(db.String(10), nullable=False)
    date             = db.Column(db.Date, nullable=False)
    aircraft_type    = db.Column(db.String(50), nullable=False)
    economy_price    = db.Column(db.Float, nullable=False)
    business_price   = db.Column(db.Float, nullable=False)
    first_price      = db.Column(db.Float, nullable=False)
    economy_seats    = db.Column(db.Integer, default=180)
    business_seats   = db.Column(db.Integer, default=36)
    first_seats      = db.Column(db.Integer, default=12)
    status           = db.Column(db.String(20), default='Scheduled')
    bookings         = db.relationship('Booking', backref='flight', lazy=True,
                                       cascade='all, delete-orphan')

    def duration(self):
        dep = datetime.strptime(self.departure_time, '%H:%M')
        arr = datetime.strptime(self.arrival_time, '%H:%M')
        diff = arr - dep
        if diff.days < 0:
            diff += timedelta(days=1)
        h = diff.seconds // 3600
        m = (diff.seconds % 3600) // 60
        return f"{h}h {m:02d}m"

    def duration_mins(self):
        dep = datetime.strptime(self.departure_time, '%H:%M')
        arr = datetime.strptime(self.arrival_time, '%H:%M')
        diff = arr - dep
        if diff.days < 0:
            diff += timedelta(days=1)
        return diff.seconds // 60

    def is_domestic(self):
        domestic_codes = {'BOM', 'DEL', 'BLR', 'MAA', 'CCU', 'HYD', 'GOI', 'JAI'}
        return self.origin_code in domestic_codes and self.destination_code in domestic_codes

    def seats_for_class(self, cls):
        return {'Economy': self.economy_seats, 'Business': self.business_seats, 'First': self.first_seats}.get(cls, 0)

    def price_for_class(self, cls):
        return {'Economy': self.economy_price, 'Business': self.business_price, 'First': self.first_price}.get(cls, 0)

    def apex_miles(self, cls):
        return int(self.price_for_class(cls) / 10)

    def __repr__(self):
        return f'<Flight {self.flight_number} {self.origin_code}-{self.destination_code} {self.date}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    id               = db.Column(db.Integer, primary_key=True)
    pnr              = db.Column(db.String(10), unique=True, nullable=False)
    flight_id        = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    passenger_name   = db.Column(db.String(100), nullable=False)
    passenger_email  = db.Column(db.String(120), nullable=False)
    passenger_phone  = db.Column(db.String(20), nullable=False)
    passport_number  = db.Column(db.String(30), nullable=False)
    seat_class       = db.Column(db.String(20), default='Economy')
    seat_number      = db.Column(db.String(10), nullable=True)
    price_paid       = db.Column(db.Float, nullable=False)
    booking_date     = db.Column(db.DateTime, default=datetime.utcnow)
    check_in_status  = db.Column(db.String(20), default='confirmed')

    def __repr__(self):
        return f'<Booking {self.pnr}>'
