# Rolling Popcorn - Movie Ticket Booking Frontend

A complete frontend for the movie ticket booking system with a modern red-black theme.

## Features

### ✅ **User Registration & Authentication**
- User registration with validation
- User login/logout functionality
- Session management

### ✅ **Movie Discovery**
- Browse all available movies
- Search and filter movies by language, city, and keywords
- Featured movies section
- Coming soon movies

### ✅ **Movie Details**
- Detailed movie information
- User ratings and reviews
- Available shows for each movie
- Write and submit reviews (for logged-in users)

### ✅ **Show Selection**
- View available shows for selected movies
- Show times, theaters, and pricing
- Seat availability information

### ✅ **Seat Selection**
- Interactive seat layout (10 rows × 15 seats)
- Visual seat status (available, selected, booked)
- Real-time booking summary
- Seat legend for clarity

### ✅ **Payment & Booking**
- Secure payment form
- Booking summary
- Credit card information collection
- Booking confirmation

### ✅ **Ticket Management**
- Digital ticket generation
- QR code for entry
- Print functionality
- Booking details display

## File Structure

```
frontend/
├── assets/                 # Images and media files
│   ├── rollingpopcornlogo.png
│   ├── movie posters (various .jpg files)
│   └── city icons (.png files)
├── styles/
│   └── styles.css         # Main CSS with red-black theme
├── scripts/
│   └── app.js            # Main JavaScript functionality
├── index.html            # Home page with movie listings
├── login.html            # User login page
├── register.html         # User registration page
├── movie.html            # Movie detail page
├── seat.html             # Seat selection page
├── payment.html          # Payment processing page
├── ticket.html           # Ticket confirmation page
└── README.md            # This file
```

## Design Theme

The frontend uses a **red-black theme** with:
- **Primary Red**: `#cc1e36`
- **Dark Red**: `#a91729`
- **Black**: `#1a1a1a`
- **Dark Gray**: `#2d2d2d`
- **Light Gray**: `#404040`
- **White Text**: `#ffffff`

## API Integration

The frontend integrates with the Django backend API endpoints:

- **Authentication**: `/auth/register/`, `/auth/login/`, `/auth/logout/`
- **Movies**: `/home/`, `/movies/<id>/`, `/movies/<id>/reviews/`
- **Shows**: `/shows/`, `/shows/<id>/`
- **Bookings**: `/bookings/create/`, `/bookings/<id>/`
- **Reviews**: `/reviews/create/`

## Usage

1. **Start the Django backend** (make sure it's running on `http://127.0.0.1:8000`)
2. **Open the frontend** by navigating to the `frontend/` directory
3. **Browse movies** on the home page
4. **Register/Login** to book tickets
5. **Select a movie** to view details and available shows
6. **Choose seats** from the interactive seat layout
7. **Complete payment** to confirm booking
8. **View/Print ticket** with booking confirmation

## Key Features

### Responsive Design
- Mobile-friendly layout
- Adaptive grid systems
- Touch-friendly interactions

### User Experience
- Loading indicators
- Error handling
- Success messages
- Form validation

### Security
- CSRF token handling
- Session management
- Input validation

### Accessibility
- Semantic HTML
- Keyboard navigation
- Screen reader friendly

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development

To modify the frontend:

1. **CSS**: Edit `styles/styles.css` for styling changes
2. **JavaScript**: Edit `scripts/app.js` for functionality
3. **HTML**: Edit individual `.html` files for structure
4. **Assets**: Add new images to `assets/` directory

## Notes

- The frontend requires the Django backend to be running
- All API calls are made to `http://127.0.0.1:8000`
- Session data is stored in browser sessionStorage
- CSRF tokens are automatically handled for Django compatibility
