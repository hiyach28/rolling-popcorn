"""
URL configuration for the booking app.
Defines all API endpoints for the movie booking system.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.login_view, name='user-login'),
    path('auth/logout/', views.logout_view, name='user-logout'),
    path('auth/profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Theater endpoints
    path('theaters/', views.TheaterListView.as_view(), name='theater-list'),
    
    # Movie endpoints
    path('home/', views.MovieListView.as_view(), name='movie-list'), #home page
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie-detail'),
    path('movies/<int:movie_id>/reviews/', views.MovieReviewsView.as_view(), name='movie-reviews'),
    
    # Show endpoints
    path('shows/', views.ShowListView.as_view(), name='show-list'),
    path('shows/<int:pk>/', views.ShowDetailView.as_view(), name='show-detail'),
    
    # Booking endpoints
    path('bookings/', views.UserBookingsView.as_view(), name='user-bookings'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    
    # Review endpoints
    path('reviews/', views.UserReviewsView.as_view(), name='user-reviews'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    
    # Admin endpoints
    path('dashboard/movies/create/', views.AdminMovieCreateView.as_view(), name='admin-movie-create'),
    path('dashboard/theaters/create/', views.AdminTheaterCreateView.as_view(), name='admin-theater-create'),
    path('dashboard/shows/create/', views.AdminShowCreateView.as_view(), name='admin-show-create'),
]