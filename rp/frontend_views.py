"""
Frontend views for serving HTML pages and handling frontend routing.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os

def serve_frontend(request, page='index.html'):
    """
    Serve frontend HTML pages from the pages directory.
    """
    # Map common routes to HTML files
    page_mapping = {
        '': 'index.html',
        'index': 'index.html',
        'home': 'index.html',
        'movies': 'movie.html',
        'movie': 'movie.html',
        'shows': 'shows.html',
        'booking': 'booking.html',
        'bookings': 'booking.html',
        'seat': 'seat.html',
        'seats': 'seat.html',
        'payment': 'payment.html',
        'ticket': 'ticket.html',
        'login': 'login.html',
        'register': 'register.html',
        'profile': 'profile.html',
        'dashboard': 'dashboard.html',
    }
    
    # Get the page name from the URL
    if page in page_mapping:
        html_file = page_mapping[page]
    else:
        html_file = f"{page}.html"
    
    # Path to the frontend pages directory
    frontend_path = os.path.join(settings.BASE_DIR, 'frontend', 'pages')
    html_path = os.path.join(frontend_path, html_file)
    
    # Check if the HTML file exists
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    else:
        # Return 404 for non-existent pages
        return HttpResponse('<h1>Page Not Found</h1>', status=404)

def index(request):
    """Serve the main index page."""
    return serve_frontend(request, 'index')

def movies(request):
    """Serve the movies page."""
    return serve_frontend(request, 'movies')

def movie_detail(request, movie_id=None):
    """Serve the movie detail page."""
    return serve_frontend(request, 'movie')

def shows(request):
    """Serve the shows page."""
    return serve_frontend(request, 'shows')

def booking(request):
    """Serve the booking page."""
    return serve_frontend(request, 'booking')

def seat_selection(request):
    """Serve the seat selection page."""
    return serve_frontend(request, 'seat')

def payment(request):
    """Serve the payment page."""
    return serve_frontend(request, 'payment')

def ticket(request):
    """Serve the ticket page."""
    return serve_frontend(request, 'ticket')

def login(request):
    """Serve the login page."""
    return serve_frontend(request, 'login')

def register(request):
    """Serve the register page."""
    return serve_frontend(request, 'register')

def profile(request):
    """Serve the profile page."""
    return serve_frontend(request, 'profile')

def dashboard(request):
    """Serve the dashboard page."""
    return serve_frontend(request, 'dashboard')
