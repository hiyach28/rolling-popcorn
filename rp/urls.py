from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import frontend_views
import os

urlpatterns = [
    path('admin/', admin.site.urls),

    # All API endpoints under /api/
    path('api/', include('booking.urls')),

    # Frontend page routes
    path('', frontend_views.index, name='index'),
    path('movie/<int:movie_id>/', frontend_views.movie_detail, name='movie-detail-page'),
    path('movies/', frontend_views.movies, name='movies-page'),
    path('shows/', frontend_views.shows, name='shows-page'),
    path('booking/', frontend_views.booking, name='booking-page'),
    path('bookings/', frontend_views.booking, name='bookings-page'),
    path('seat/', frontend_views.seat_selection, name='seat-page'),
    path('payment/', frontend_views.payment, name='payment-page'),
    path('ticket/', frontend_views.ticket, name='ticket-page'),
    path('login/', frontend_views.login, name='login-page'),
    path('register/', frontend_views.register, name='register-page'),
    path('profile/', frontend_views.profile, name='profile-page'),
    path('dashboard/', frontend_views.dashboard, name='dashboard-page'),
    path('theaters/', frontend_views.theaters, name='theaters-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve frontend assets directly
    urlpatterns += static('/frontend/', document_root=os.path.join(settings.BASE_DIR, 'frontend'))
