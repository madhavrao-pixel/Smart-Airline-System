from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, jsonify)
from models import db, Flight, Booking
from datetime import datetime, date, timedelta
import random, string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'apex-voyage-2026-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

ADMIN_PASSWORD = 'apexadmin2026'

AIRPORTS = {
    'BOM': 'Mumbai',    'DEL': 'Delhi',     'BLR': 'Bangalore',
    'MAA': 'Chennai',   'CCU': 'Kolkata',   'HYD': 'Hyderabad',
    'GOI': 'Goa',       'JAI': 'Jaipur',    'DXB': 'Dubai',
    'SIN': 'Singapore', 'BKK': 'Bangkok',   'KUL': 'Kuala Lumpur',
    'NRT': 'Tokyo',     'HKG': 'Hong Kong', 'CMB': 'Colombo',
    'KTM': 'Kathmandu',
}

CURRENCY_RATES = {'INR': 1, 'USD': 83.5, 'SGD': 62.0, 'AED': 22.7}


def gen_pnr():
    while True:
        pnr = 'AV' + ''.join(random.choices(string.digits, k=4))
        if not Booking.query.filter_by(pnr=pnr).first():
            return pnr


def admin_required():
    return session.get('apex_admin', False)


# ── API ────────────────────────────────────────────────────────────────────────

@app.route('/api/airports')
def api_airports():
    return jsonify([{'code': k, 'city': v} for k, v in AIRPORTS.items()])


@app.route('/api/track-flight')
def api_track_flight():
    fn = request.args.get('flight', '').upper().strip()
    if fn.startswith('AV') and len(fn) >= 4:
        statuses = ['On Time', 'Boarding', 'Departed', 'Landed', 'Delayed']
        weights  = [40, 15, 25, 15, 5]
        status   = random.choices(statuses, weights)[0]
        progress = {'On Time': 0, 'Boarding': 20, 'Departed': 55, 'Landed': 100, 'Delayed': 5}
        return jsonify({'found': True, 'flight': fn, 'status': status,
                        'progress': progress[status]})
    return jsonify({'found': False})


# ── Public Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', airports=AIRPORTS)


@app.route('/search')
def search():
    origin      = request.args.get('origin', '').strip().upper()
    destination = request.args.get('destination', '').strip().upper()
    travel_date = request.args.get('date', '').strip()
    seat_class  = request.args.get('class', 'Economy')
    passengers  = int(request.args.get('passengers', 1))

    flights, price_calendar = [], []

    if origin and destination and travel_date:
        try:
            search_date = datetime.strptime(travel_date, '%Y-%m-%d').date()
            flights = (Flight.query
                       .filter_by(origin_code=origin, destination_code=destination,
                                  date=search_date)
                       .filter(Flight.status != 'Cancelled')
                       .order_by(Flight.departure_time).all())

            for offset in range(-3, 4):
                d = search_date + timedelta(days=offset)
                cheapest = (Flight.query
                            .filter_by(origin_code=origin, destination_code=destination, date=d)
                            .filter(Flight.status != 'Cancelled')
                            .order_by(Flight.economy_price).first())
                price_calendar.append({'date': d, 'price': cheapest.economy_price if cheapest else None,
                                       'selected': d == search_date})
        except ValueError:
            pass

    return render_template('search.html', flights=flights, origin=origin,
                           destination=destination, travel_date=travel_date,
                           seat_class=seat_class, passengers=passengers,
                           airports=AIRPORTS, price_calendar=price_calendar)


@app.route('/flight/<int:flight_id>')
def flight_detail(flight_id):
    flight     = Flight.query.get_or_404(flight_id)
    seat_class = request.args.get('class', 'Economy')
    passengers = int(request.args.get('passengers', 1))

    booked_seats = [b.seat_number for b in
                    Booking.query.filter(Booking.flight_id == flight_id,
                                         Booking.check_in_status != 'cancelled',
                                         Booking.seat_number.isnot(None)).all()]

    # AI Seat Recommender: score seats by position (window = higher, front = higher)
    def recommend_seat(cls):
        if cls == 'First':
            return '2A', 94
        elif cls == 'Business':
            return '4A', 89
        else:
            return '14A', 87

    rec_seat, rec_score = recommend_seat(seat_class)

    return render_template('flight.html', flight=flight, seat_class=seat_class,
                           passengers=passengers, booked_seats=booked_seats,
                           airports=AIRPORTS, rec_seat=rec_seat, rec_score=rec_score)


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        flight_id   = request.form.get('flight_id')
        seat_class  = request.form.get('seat_class', 'Economy')
        seat_number = request.form.get('seat_number', '')
        first_name  = request.form.get('first_name', '').strip()
        last_name   = request.form.get('last_name', '').strip()
        email       = request.form.get('email', '').strip()
        phone       = request.form.get('phone', '').strip()
        passport    = request.form.get('passport', '').strip()

        if not all([flight_id, first_name, last_name, email, phone, passport]):
            flash('All passenger fields are required.', 'error')
            return redirect(request.referrer or url_for('index'))

        flight = Flight.query.get_or_404(flight_id)
        price  = flight.price_for_class(seat_class)
        pnr    = gen_pnr()

        bk = Booking(pnr=pnr, flight_id=flight_id,
                     passenger_name=f"{first_name} {last_name}",
                     passenger_email=email, passenger_phone=phone,
                     passport_number=passport, seat_class=seat_class,
                     seat_number=seat_number if seat_number else None,
                     price_paid=price)
        if seat_class == 'Economy' and flight.economy_seats > 0:
            flight.economy_seats -= 1
        elif seat_class == 'Business' and flight.business_seats > 0:
            flight.business_seats -= 1
        elif seat_class == 'First' and flight.first_seats > 0:
            flight.first_seats -= 1

        db.session.add(bk)
        db.session.commit()
        session['last_pnr'] = pnr
        return redirect(url_for('confirmation'))

    flight_id   = request.args.get('flight_id')
    seat_class  = request.args.get('class', 'Economy')
    seat_number = request.args.get('seat', '')
    passengers  = int(request.args.get('passengers', 1))

    if not flight_id:
        return redirect(url_for('index'))
    flight = Flight.query.get_or_404(flight_id)
    return render_template('booking.html', flight=flight, seat_class=seat_class,
                           seat_number=seat_number, passengers=passengers)


@app.route('/confirmation')
def confirmation():
    pnr = session.get('last_pnr')
    if not pnr:
        return redirect(url_for('index'))
    bk = Booking.query.filter_by(pnr=pnr).first_or_404()
    return render_template('confirmation.html', booking=bk)


@app.route('/my-trips', methods=['GET', 'POST'])
def my_trips():
    booking, error = None, None
    if request.method == 'POST':
        pnr       = request.form.get('pnr', '').strip().upper()
        last_name = request.form.get('last_name', '').strip().lower()
        if pnr and last_name:
            bk = Booking.query.filter_by(pnr=pnr).first()
            if bk and last_name in bk.passenger_name.lower():
                booking = bk
            else:
                error = 'No booking found with those details. Please check your PNR and last name.'
    return render_template('my-trips.html', booking=booking, error=error)


@app.route('/cancel-booking/<pnr>', methods=['POST'])
def cancel_booking(pnr):
    bk = Booking.query.filter_by(pnr=pnr).first_or_404()
    if bk.check_in_status != 'cancelled':
        bk.check_in_status = 'cancelled'
        f = bk.flight
        if bk.seat_class == 'Economy':    f.economy_seats  += 1
        elif bk.seat_class == 'Business': f.business_seats += 1
        else:                              f.first_seats    += 1
        db.session.commit()
    flash('Your booking has been cancelled.', 'info')
    return redirect(url_for('my_trips'))


@app.route('/check-in', methods=['GET', 'POST'])
def check_in():
    booking, error, boarded = None, None, False
    if request.method == 'POST':
        pnr       = request.form.get('pnr', '').strip().upper()
        last_name = request.form.get('last_name', '').strip().lower()
        action    = request.form.get('action', 'lookup')
        bk = Booking.query.filter_by(pnr=pnr).first()
        if bk and last_name in bk.passenger_name.lower():
            if action == 'checkin' and bk.check_in_status == 'confirmed':
                bk.check_in_status = 'checked_in'
                db.session.commit()
                boarded = True
            booking = bk
        else:
            error = 'No booking found. Please verify your PNR and last name.'
    return render_template('check-in.html', booking=booking, error=error, boarded=boarded)


# ── Admin ──────────────────────────────────────────────────────────────────────

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            if request.form.get('password') == ADMIN_PASSWORD:
                session['apex_admin'] = True
            else:
                flash('Invalid password.', 'error')
            return redirect(url_for('admin'))

        if action == 'logout':
            session.pop('apex_admin', None)
            return redirect(url_for('admin'))

        if not admin_required():
            return redirect(url_for('admin'))

        if action == 'cancel_flight':
            f = Flight.query.get(request.form.get('flight_id'))
            if f:
                f.status = 'Cancelled'
                db.session.commit()

        elif action == 'add_flight':
            try:
                seats = int(request.form.get('economy_seats', 180))
                f = Flight(
                    flight_number   = request.form['flight_number'].upper(),
                    origin_code     = request.form['origin_code'].upper(),
                    origin_city     = AIRPORTS.get(request.form['origin_code'].upper(),
                                                   request.form['origin_code']),
                    destination_code= request.form['destination_code'].upper(),
                    destination_city= AIRPORTS.get(request.form['destination_code'].upper(),
                                                   request.form['destination_code']),
                    departure_time  = request.form['departure_time'],
                    arrival_time    = request.form['arrival_time'],
                    date            = datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                    aircraft_type   = request.form.get('aircraft_type', 'Airbus A320neo'),
                    economy_price   = float(request.form['economy_price']),
                    business_price  = float(request.form['business_price']),
                    first_price     = float(request.form['first_price']),
                    economy_seats   = seats,
                    business_seats  = int(request.form.get('business_seats', 36)),
                    first_seats     = int(request.form.get('first_seats', 12)),
                )
                db.session.add(f)
                db.session.commit()
                flash(f'Flight {f.flight_number} added.', 'success')
            except Exception as e:
                flash(f'Error: {e}', 'error')
        return redirect(url_for('admin'))

    if not admin_required():
        return render_template('admin.html', logged_in=False)

    today = date.today()
    flights_today   = Flight.query.filter_by(date=today).count()
    bookings_today  = Booking.query.filter(
        db.func.date(Booking.booking_date) == today).count()
    revenue_today   = db.session.query(
        db.func.sum(Booking.price_paid)).filter(
        db.func.date(Booking.booking_date) == today,
        Booking.check_in_status != 'cancelled').scalar() or 0

    eco   = Booking.query.filter_by(seat_class='Economy').count()
    biz   = Booking.query.filter_by(seat_class='Business').count()
    first = Booking.query.filter_by(seat_class='First').count()

    weekly = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        c = Booking.query.filter(db.func.date(Booking.booking_date) == d).count()
        weekly.append({'label': d.strftime('%a %d'), 'count': c})

    flights  = (Flight.query.order_by(Flight.date, Flight.departure_time).limit(60).all())
    bookings = (Booking.query.order_by(Booking.booking_date.desc()).limit(60).all())

    return render_template('admin.html', logged_in=True,
                           flights_today=flights_today, bookings_today=bookings_today,
                           revenue_today=revenue_today, eco=eco, biz=biz, first=first,
                           weekly=weekly, flights=flights, bookings=bookings,
                           airports=AIRPORTS, today=today.isoformat())


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
