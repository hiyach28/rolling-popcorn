
# Django REST Framework serializers for API endpoints.
# Handles data serialization and validation for all models.

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Theater, Screen, Seat, Movie, Show, Booking, BookedSeat, Review, Genre


class UserRegistrationSerializer(serializers.ModelSerializer):
    #Serializer for user registration with password confirmation.

    password = serializers.CharField(write_only=True, min_length=4) #write-only true means it can not be GET
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password', 'password_confirm') #tells which fields to expect from user
        read_only_fields = ('role',)  # Users can't set role on signup unless you want them to

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm') #dont store password_confirm
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    #Serializer for user authentication.

    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    #Serializer for user profile information.

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'date_joined')
        read_only_fields = ('id', 'username', 'role', 'date_joined')


class TheaterSerializer(serializers.ModelSerializer):
    #Serializer for theater information.

    class Meta:
        model = Theater
        fields = ('id', 'name', 'city', 'location', 'total_screens')


class SeatSerializer(serializers.ModelSerializer):
    #Serializer for seat information.
    
    class Meta:
        model = Seat
        fields = ('id', 'seat_number')


class ScreenSerializer(serializers.ModelSerializer):
    """
    Serializer for screen information with seats.
    """
    seats = SeatSerializer(many=True, read_only=True)
    theater_name = serializers.CharField(source='theater.name', read_only=True)
    
    class Meta:
        model = Screen
        fields = ('id','screen_number','theater', 'theater_name', 'seat_layout', 'seats')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class MovieListSerializer(serializers.ModelSerializer):
    """
    Serializer for movie list view with basic information.
    """
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ('id', 'name', 'duration', 'genres', 'poster', 'language', 'release_date', 'average_rating', 'total_reviews')


class MovieDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed movie view with reviews.
    """
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    reviews = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ('id', 'name', 'description', 'genres', 'language', 'duration', 
                 'poster', 'release_date', 'average_rating', 
                 'total_reviews', 'reviews')
    
    def get_reviews(self, obj):
        recent_reviews = obj.reviews.select_related('user').order_by('-created_at')[:5]
        return ReviewSerializer(recent_reviews, many=True).data


class ShowListSerializer(serializers.ModelSerializer):
    """
    Serializer for show listings with basic information.
    """
    movie_title = serializers.CharField(source='movie.name', read_only=True)
    # movie_poster = serializers.ImageField(source='movie.poster', read_only=True)
    theater_name = serializers.CharField(source='screen.theater.name', read_only=True)
    movie_duration = serializers.IntegerField(source='movie.duration', read_only=True)
    theater_city = serializers.CharField(source='screen.theater.city', read_only=True)
    screen_number = serializers.CharField(source='screen.screen_number', read_only=True)
    available_seats_count = serializers.SerializerMethodField()
    total_seats = serializers.ReadOnlyField()
    
    class Meta:
        model = Show
        fields = ('id', 'movie', 'movie_title', 'screen', 'movie_duration'
                 'theater_name', 'theater_city', 'screen_number', 
                 'show_time', 'price_per_seat', 'available_seats_count', 'total_seats')
    
    def get_available_seats_count(self, obj):
        return obj.available_seats.count()


class ShowDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed show view with seat availability.
    """
    movie = MovieListSerializer(read_only=True)
    screen = ScreenSerializer(read_only=True)
    available_seats = SeatSerializer(many=True, read_only=True)
    booked_seats = serializers.SerializerMethodField()
    
    class Meta:
        model = Show
        fields = ('id', 'movie', 'screen', 'show_time', 'price_per_seat', 
                 'available_seats', 'booked_seats', 'total_seats')
    
    def get_booked_seats(self, obj):
        booked_seat_ids = BookedSeat.objects.filter(
            booking__show=obj,
            booking__status='confirmed'
        ).values_list('seat_id', flat=True)
        return list(booked_seat_ids)


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new bookings.
    """
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        min_length=1
    )
    
    class Meta:
        model = Booking
        fields = ('show', 'seat_ids')
    
    def validate_seat_ids(self, value):
        """Validate that all seats exist and are available"""
        show = self.initial_data.get('show')
        if not show:
            raise serializers.ValidationError("Show is required")
        
        # Check if seats exist in the show's screen
        valid_seats = Seat.objects.filter(
            id__in=value,
            screen__shows=show
        ).values_list('id', flat=True)
        
        if len(valid_seats) != len(value):
            raise serializers.ValidationError("Some seats are invalid for this show")
        
        # Check if seats are already booked
        booked_seats = BookedSeat.objects.filter(
            seat_id__in=value,
            booking__show=show,
            booking__status='confirmed'
        ).values_list('seat_id', flat=True)
        
        if booked_seats:
            raise serializers.ValidationError("Some seats are already booked")
        
        return value
    
    def create(self, validated_data):
        seat_ids = validated_data.pop('seat_ids')
        show = validated_data['show']
        user = self.context['request'].user
        
        # Calculate total price
        total_price = len(seat_ids) * show.price_per_seat
        
        # Create booking
        booking = Booking.objects.create(
            user=user,
            show=show,
            total_price=total_price
        )
        
        # Create booked seats
        booked_seats = [
            BookedSeat(booking=booking, seat_id=seat_id)
            for seat_id in seat_ids
        ]
        BookedSeat.objects.bulk_create(booked_seats)
        
        return booking


class BookedSeatSerializer(serializers.ModelSerializer):
    #shows which seat is booked in a booking

    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    # seat_type = serializers.CharField(source='seat.seat_type', read_only=True)
    
    class Meta:
        model = BookedSeat
        fields = ('seat', 'seat_number')


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for booking information with related data.
    """
    show = ShowListSerializer(read_only=True)
    booked_seats = BookedSeatSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = ('id', 'user', 'user_name', 'show', 'total_price', 
                 'booking_time', 'status', 'booked_seats')


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for movie reviews and ratings.
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'user', 'user_name', 'movie', 'rating', 'review_text', 'created_at')
        read_only_fields = ('user',)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating movie reviews.
    """
    class Meta:
        model = Review
        fields = ('movie', 'rating', 'review_text')
    
    def validate_movie(self, value):
        """Ensure user has watched this movie before reviewing"""
        user = self.context['request'].user
        has_booking = Booking.objects.filter(
            user=user,
            show__movie=value,
            status='confirmed'
        ).exists()
        
        if not has_booking:
            raise serializers.ValidationError(
                "You can only review movies you have booked tickets for"
            )
        
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class BulkShowSerializer(serializers.Serializer):
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all())
    screen = serializers.PrimaryKeyRelatedField(queryset=Screen.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    days_of_week = serializers.ListField(child=serializers.ChoiceField(choices=[
        ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
        ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')
    ]))
    shows_per_day = serializers.IntegerField(min_value=1)
    price_per_seat = serializers.DecimalField(max_digits=10, decimal_places=2)
    