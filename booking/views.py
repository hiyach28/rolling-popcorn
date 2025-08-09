"""
Django REST Framework views for the movie booking system.
Implements all API endpoints with proper authentication and permissions.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login
from django.utils import timezone

import json

from .models import User, Theater, Screen, Movie, Show, Booking, Review
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    TheaterSerializer, ScreenSerializer, MovieListSerializer, MovieDetailSerializer,
    ShowListSerializer, ShowDetailSerializer, BookingCreateSerializer, 
    BookingSerializer, ReviewSerializer, ReviewCreateSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Creates a new user account and returns authentication token.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    API endpoint for user authentication.
    Returns user profile and authentication token on successful login.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # Get or create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    """
    API endpoint for user logout.
    Deletes the user's authentication token.
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except:
        return Response({'message': 'Logout successful'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class TheaterListView(generics.ListAPIView):
    """
    API endpoint for listing all theaters.
    Supports filtering by location.
    """
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city']
    search_fields = ['name', 'city']


class MovieListView(generics.ListAPIView):
    """
    API endpoint for listing movies with search and filter capabilities.
    Supports filtering by genre, language, and theater location.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'language']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'title']
    ordering = ['-release_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by theater location if provided
        theater_city = self.request.query_params.get('theater_city')
        if theater_location:
            queryset = queryset.filter(
                shows__screen__theater__city__icontains=theater_city
            ).distinct()
        
        # Filter by show date if provided
        show_date = self.request.query_params.get('show_date')
        if show_date:
            queryset = queryset.filter(
                shows__show_time__date=show_date
            ).distinct()
        
        return queryset


class MovieDetailView(generics.RetrieveAPIView):
    """
    API endpoint for detailed movie information including reviews.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer
    permission_classes = [permissions.AllowAny]

class ShowListView(generics.ListAPIView):
    """
    API endpoint for listing shows with filtering capabilities.
    Supports filtering by theater, theater city, show date, and date range.
    """
    queryset = Show.objects.select_related('movie', 'screen__theater').all()
    serializer_class = ShowListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['screen__theater']  # you can add more if needed
    ordering_fields = ['show_time', 'price_per_seat']
    ordering = ['show_time']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by theater city (location)
        theater_city = self.request.query_params.get('theater_city')
        if theater_city:
            queryset = queryset.filter(screen__theater__location__icontains=theater_city)

        # Filter by exact show date
        show_date = self.request.query_params.get('show_date')
        if show_date:
            queryset = queryset.filter(show_time__date=show_date)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(show_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(show_time__date__lte=end_date)

        # Only show future shows by default if no start_date provided
        if not start_date and not show_date:
            queryset = queryset.filter(show_time__gte=timezone.now())

        return queryset


class ShowDetailView(generics.RetrieveAPIView):
    """
    API endpoint for detailed show information including seat availability.
    """
    queryset = Show.objects.select_related('movie', 'screen__theater').prefetch_related('screen__seats')
    serializer_class = ShowDetailSerializer
    permission_classes = [permissions.AllowAny]


class BookingCreateView(generics.CreateAPIView):
    """
    API endpoint for creating new bookings.
    Validates seat availability and creates booking with confirmation email.
    """
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create booking
        booking = serializer.save()
        
        # Release seat locks after successful booking
        show_id = request.data.get('show')
        seat_ids = request.data.get('seat_ids', [])
        
        seat_manager = SeatLockManager(redis_client)
        for seat_id in seat_ids:
            seat_manager.release_seat(show_id, seat_id, request.user.id)
        
        # Send confirmation email asynchronously
        send_booking_confirmation_email.delay(booking.id)
        
        # Return booking details
        booking_serializer = BookingSerializer(booking)
        return Response({
            'booking': booking_serializer.data,
            'message': 'Booking created successfully. Confirmation email will be sent shortly.'
        }, status=status.HTTP_201_CREATED)


class UserBookingsView(generics.ListAPIView):
    """
    API endpoint for listing user's booking history.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related('show__movie', 'show__screen__theater').prefetch_related('booked_seats__seat').order_by('-booking_time')


class BookingDetailView(generics.RetrieveAPIView):
    """
    API endpoint for detailed booking information.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_booking(request, booking_id):
    """
    API endpoint for cancelling bookings.
    Only allows cancellation before show time.
    """
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if booking can be cancelled (before show time)
    if booking.show.show_time <= timezone.now():
        return Response({
            'error': 'Cannot cancel booking after show time'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if booking.status == 'cancelled':
        return Response({
            'error': 'Booking is already cancelled'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    booking.status = 'cancelled'
    booking.save()
    
    return Response({
        'message': 'Booking cancelled successfully'
    })


class ReviewCreateView(generics.CreateAPIView):
    """
    API endpoint for creating movie reviews.
    """
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class MovieReviewsView(generics.ListAPIView):
    """
    API endpoint for listing reviews for a specific movie.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return Review.objects.filter(movie_id=movie_id).select_related('user').order_by('-created_at')


class UserReviewsView(generics.ListAPIView):
    """
    API endpoint for listing user's reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('movie').order_by('-created_at')


# Admin-only views for managing content
class AdminMovieCreateView(generics.CreateAPIView):
    """
    Admin-only API endpoint for creating movies.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.user.role != 'admin':
            self.permission_denied(self.request, message="Admin access required")
        return super().get_permissions()


class AdminTheaterCreateView(generics.CreateAPIView):
    """
    Admin-only API endpoint for creating theaters.
    """
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.user.role != 'admin':
            self.permission_denied(self.request, message="Admin access required")
        return super().get_permissions()


class AdminShowCreateView(generics.CreateAPIView):
    """
    Admin-only API endpoint for creating shows.
    """
    queryset = Show.objects.all()
    serializer_class = ShowDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.user.role != 'admin':
            self.permission_denied(self.request, message="Admin access required")
        return super().get_permissions()