# Rolling Popcorn 🍿

A full-stack movie ticket booking web app built with Django REST Framework and vanilla HTML/CSS/JS.

---

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework, MySQL
- **Frontend**: HTML, CSS, Vanilla JavaScript (served by Django)
- **Auth**: Token-based authentication (DRF AuthToken)
- **Other**: django-cors-headers, django-filter, Pillow, python-dotenv

---

## Features

### Users
- Register and login with token auth
- View and update profile
- Role-based access: `user` and `admin` (Theatre Manager)

### Movies
- Browse all movies with poster images, genres, language, rating
- Search by name, filter by language and city
- Movie detail page with synopsis and reviews
- Average rating calculated from user reviews

### Theaters & Shows
- Browse theaters by city
- View shows per movie with date/time filters
- Show detail with real-time seat availability

### Seat Booking
- Interactive seat layout (rows A–C, grouped by screen)
- Visual states: available, selected, booked
- Booking summary with total price calculation
- Proceed to payment flow

### Payment & Tickets
- Simulated payment (card, UPI, net banking, wallet)
- Booking confirmation with ticket view
- Download or print ticket
- Cancel booking (before show time)

### Reviews
- Submit a review only if you've booked that movie
- Rating out of 10
- Reviews shown on movie detail page

### Theatre Manager Dashboard
- Admin-only dashboard
- Bulk schedule shows across a date range
- Create movies, theaters, shows via API

---

## Project Structure

```
rolling-popcorn/
├── booking/                  # Django app
│   ├── models.py             # User, Movie, Theater, Screen, Seat, Show, Booking, Review
│   ├── views.py              # All API views
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # API routes (mounted at /api/)
│   ├── utils.py              # Show time generator, seat layout helper
│   └── fixtures/
│       └── sample_data.json  # Seed data (movies, theaters, shows, seats)
├── frontend/
│   ├── pages/                # HTML pages
│   │   ├── index.html        # Home / movie listing
│   │   ├── movie.html        # Movie detail + shows
│   │   ├── seat.html         # Seat selection
│   │   ├── payment.html      # Payment
│   │   ├── ticket.html       # Booking confirmation
│   │   ├── booking.html      # My bookings
│   │   ├── theaters.html     # Theater listing
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── dashboard.html    # Theatre manager dashboard
│   └── assets/
│       ├── css/styles.css    # Red-black theme
│       ├── js/app.js         # All frontend logic + API calls
│       └── images/           # Movie posters, banners, city icons
├── rp/
│   ├── settings.py           # Django settings (reads from .env)
│   ├── urls.py               # Root URL config
│   └── frontend_views.py     # Serves HTML pages
├── .env.example              # Environment variable template
├── requirements.txt
└── manage.py
```

---

## API Endpoints

All endpoints are prefixed with `/api/`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login, returns token |
| POST | `/api/auth/logout/` | Yes | Logout |
| GET/PATCH | `/api/auth/profile/` | Yes | View/update profile |
| GET | `/api/theaters/` | No | List theaters (filter: city) |
| GET | `/api/home/` | No | List movies (filter: language, city, date) |
| GET | `/api/movies/<id>/` | No | Movie detail |
| GET | `/api/movies/<id>/reviews/` | No | Movie reviews |
| GET | `/api/shows/` | No | List shows (filter: movie, city, date) |
| GET | `/api/shows/<id>/` | No | Show detail with seat availability |
| GET | `/api/bookings/` | Yes | User's booking history |
| POST | `/api/bookings/create/` | Yes | Create booking |
| GET | `/api/bookings/<id>/` | Yes | Booking detail |
| POST | `/api/bookings/<id>/cancel/` | Yes | Cancel booking |
| GET | `/api/reviews/` | Yes | User's reviews |
| POST | `/api/reviews/create/` | Yes | Submit review |
| POST | `/api/dashboard/bulk-add-shows/` | Admin | Bulk schedule shows |
| POST | `/api/dashboard/movies/create/` | Admin | Create movie |
| POST | `/api/dashboard/theaters/create/` | Admin | Create theater |

---

## Local Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+

### Steps

**1. Clone and create virtual environment**
```bash
git clone https://github.com/hiyach28/rolling-popcorn.git
cd rolling-popcorn
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment**
```bash
cp .env.example .env
```
Edit `.env` with your values:
```
SECRET_KEY=your-secret-key
DB_NAME=rollingpopcorn
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

**4. Create MySQL database**
```sql
CREATE DATABASE rollingpopcorn CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Load sample data**
```bash
python manage.py loaddata booking/fixtures/sample_data.json
```

**7. Create a superuser (optional)**
```bash
python manage.py createsuperuser
```

**8. Start the server**
```bash
python manage.py runserver
```

Open `http://localhost:8000` in your browser.

---made by Hiya 