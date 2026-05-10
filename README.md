# ✈ Apex Voyage — Premium Airline Booking System

> **Where India Meets Asia** — A full-stack airline web application built with Python Flask and SQLite.

---

## 🌟 Features

### Passenger
- **Flight Search** — Search by origin, destination, and date with a 7-day price calendar
- **Seat Selection** — Interactive seat map (First 1-1 / Business 2-2 / Economy 3-3 layout)
- **3-Step Booking** — Passenger info → Extras → Simulated payment
- **Boarding Pass** — Auto-generated PNR with QR placeholder on confirmation
- **My Trips** — Retrieve and manage bookings via PNR + last name
- **Online Check-In** — Check in and generate boarding pass

### Smart Features
- 🤖 **AI Seat Recommender** — Suggests best seat per class with satisfaction score
- 📈 **Dynamic Pricing Badges** — "Price rising" or "Best time to book" based on seat availability
- 📡 **Real-Time Flight Tracker** — Enter flight number on homepage to get live status
- 💱 **Multi-Currency Toggle** — Switch between INR / USD / SGD / AED
- ⭐ **Apex Miles** — Earn 1 mile per ₹10 spent, shown on every flight card

### Admin Panel (`/admin`)
- Stats: flights today, bookings today, revenue, total bookings
- Weekly bookings bar chart + class distribution pie chart (Chart.js)
- Flights table with add / cancel actions
- Bookings table with search filter

---

## 🗂 Project Structure

```
apex-voyage/
├── app.py              # Flask app — all routes and API endpoints
├── models.py           # SQLAlchemy models (Flight, Booking)
├── seed.py             # Database seeder — generates 3,078 flights
├── requirements.txt    # Python dependencies
├── static/
│   ├── logo.svg        # SVG brand logo
│   ├── css/
│   │   ├── main.css    # Global styles, hero, navbar, homepage
│   │   ├── search.css  # Search results, filters, flight cards
│   │   ├── booking.css # Seat map, booking form, confirmation, boarding pass
│   │   └── admin.css   # Admin dashboard
│   └── js/
│       ├── main.js     # Autocomplete, currency switcher, flight tracker, animations
│       ├── search.js   # Sort, filters, price slider, skeleton loading
│       ├── seat-map.js # Interactive seat map rendering and selection
│       └── admin.js    # Chart.js charts, table search, modals
└── templates/
    ├── base.html         # Base layout with navbar and footer
    ├── index.html        # Homepage with search widget
    ├── search.html       # Search results page
    ├── flight.html       # Flight detail + seat map
    ├── booking.html      # Multi-step booking form
    ├── confirmation.html # Boarding pass confirmation
    ├── my-trips.html     # Manage bookings
    ├── check-in.html     # Online check-in
    └── admin.html        # Admin dashboard
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/madhavrao-pixel/Smart-Airline-System.git
cd Smart-Airline-System
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed the database
```bash
python seed.py
```
This generates **3,078 flights** across 81 days (May 11 – Jul 30, 2026) on 38 routes.

### 4. Run the app
```bash
python app.py
```
Open **http://127.0.0.1:5000**

---

## 🔐 Admin Access

| URL | `/admin` |
|-----|----------|
| Password | `apexadmin2026` |

---

## ✈ Sample Search

| Field | Value |
|-------|-------|
| From | `BOM` (Mumbai) |
| To | `SIN` (Singapore) |
| Date | `2026-06-05` |
| Class | Economy / Business / First |

---

## 🗄 Database Models

### Flight
| Field | Type | Description |
|-------|------|-------------|
| flight_number | String | e.g. AV101 |
| origin_code / destination_code | String | IATA codes |
| date | Date | Flight date |
| departure_time / arrival_time | String | HH:MM format |
| aircraft_type | String | A380, 787, A320neo, 777X |
| economy_price / business_price / first_price | Float | Per-seat price in INR |
| economy_seats / business_seats / first_seats | Integer | Available seats |
| status | String | Scheduled / Cancelled |

### Booking
| Field | Type | Description |
|-------|------|-------------|
| pnr | String | 6-char unique reference (e.g. AV1234) |
| passenger_name / email / phone | String | Passenger details |
| passport_number | String | Passport ID |
| seat_class / seat_number | String | Class and assigned seat |
| price_paid | Float | Amount paid in INR |
| check_in_status | String | confirmed / checked_in / cancelled |

---

## 🌏 Routes Covered

### Domestic (India)
`BOM ↔ DEL` · `BOM ↔ BLR` · `DEL ↔ MAA` · `DEL ↔ CCU` · `BLR ↔ HYD` · `BOM ↔ GOI` · `DEL ↔ JAI` · `MAA ↔ CCU`

### International (Asia)
`BOM → DXB` · `DEL → SIN` · `BOM → BKK` · `DEL → KUL` · `MAA → SIN` · `BOM → NRT` · `DEL → HKG` · `BLR → SIN` · `BOM → CMB` · `DEL → KTM`

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python Flask |
| Database | SQLite + SQLAlchemy |
| Frontend | HTML5, Custom CSS3, Vanilla JS |
| Charts | Chart.js |
| Templates | Jinja2 |

---

## 🎨 Brand Identity

- **Primary:** Deep Navy `#0A1628`
- **Accent Gold:** `#C9A84C`
- **Accent Saffron:** `#FF6B35`
- **Design style:** Emirates-inspired, India-themed, glassmorphism UI

---

*Built with Python Flask · © 2026 Apex Voyage*
