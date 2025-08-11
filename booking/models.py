from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password

# Create your models here.


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds phone number and role fields for our booking system.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Theater Manager'),
    ]
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

    

class Theater(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    location = models.CharField(max_length=100, null=False)
    total_screens = models.IntegerField(null=False) #3 screens
    city = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = 'theaters'
        indexes = [
            models.Index(fields=['city']),  # For location-based searches
        ]

    def __str__(self):
        return self.name
    
class Screen(models.Model):
    # STATUS =(
    #     (1, 'Active'),
    #     (0, 'Inactive')
    # )
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='screens')
    screen_number = models.CharField(max_length=20)
    seat_layout = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'screens'
        unique_together = ['theater', 'screen_number']
    
    def __str__(self):
        return f"{self.theater.name} - Screen {self.screen_number}"
    
class Seat(models.Model):

     screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seats')
     seat_number = models.CharField(max_length=10)
    
     class Meta:
        db_table = 'seats'
        unique_together = ['screen', 'seat_number']
    
     def __str__(self):
        return f"{self.screen} - Seat {self.seat_number} ({self.seat_type})"
     
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
class Movie(models.Model):
    # STATUS =(
    #     (1, 'Active'),
    #     (0, 'Inactive')
    # )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True, blank=True)  # Optional field for movie description
    genres = models.ManyToManyField(Genre, related_name='movies')
    duration = models.IntegerField(null=False)  # Duration in minutes
    poster = models.ImageField(upload_to='posters/', blank=True)  
    language = models.CharField(max_length=50, null=False)
    release_date = models.DateField(null=False)
    # status = models.BooleanField(choices = STATUS, default=1)  # True if movie is active, False if inactive

    class Meta:
        db_table = 'movies'
        indexes = [
            models.Index(fields=['name']),  # For title searches
            models.Index(fields=['genre']),  # For genre filtering
            models.Index(fields=['language']),  # For language filtering
            models.Index(fields=['release_date']),  # For date filtering
        ]
    
    def __str__(self):
        return f"{self.title} ({self.language})"
    
    @property
    def average_rating(self):
        """Calculate average rating from user reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def total_reviews(self):
        """Get total number of reviews"""
        return self.reviews.count()
    

class Show(models.Model):
    id = models.AutoField(primary_key=True)
    movie= models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='shows')  # movie can access show using keyword 'shows' eg obj.show
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='shows')  # screen can access show using keyword 'shows' eg obj.show
    show_time = models.DateTimeField(null=False)
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2, null=False)  # Base price per seat for the sho

    class Meta:
        db_table = 'shows'
        indexes = [
            models.Index(fields=['show_time']),  # For time-based queries
            models.Index(fields=['movie', 'show_time']),  # For movie show listings
        ]
    
    def __str__(self):
        return f"{self.movie.title} - {self.screen} at {self.show_time}"
    
    @property
    def available_seats(self):
        """Get list of available seats for this show"""
        booked_seat_ids = BookedSeat.objects.filter(
            booking__show=self,
            booking__status='confirmed'
        ).values_list('seat_id', flat=True)
        
        return self.screen.seats.exclude(id__in=booked_seat_ids)
    
    @property
    def total_seats(self):
        """Get total number of seats in the screen"""
        return self.screen.seats.count()
    
    @property
    def booked_seats_count(self):
        """Get number of booked seats for this show"""
        return BookedSeat.objects.filter(
            booking__show=self,
            booking__status='confirmed'
        ).count()
   
class Booking(models.Model):
    STATUS = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.AutoField(primary_key=True)
    user = models.IntegerField(null=False)  # Assuming user_id is an integer representing the user's ID
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='bookings')  # show can access booking using keyword 'bookings' eg obj.booking
    booking_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)  # Total price for the bookin
    status = models.CharField(max_length=10, choices = STATUS, default='confirmed')  # True if booking is confirmed, False if cancelled

    class Meta:
        db_table = 'bookings'
        indexes = [
            models.Index(fields=['user', 'booking_time']),  # For user booking history
            models.Index(fields=['show', 'status']),  # For show booking queries
        ]

    def __str__(self):
        return f"Booking {self.id} for Show {self.show.show_time} in Screen {self.show.screen.screen_number}"
   
class BookedSeat(models.Model):
    id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_seats')  # booking can access booked_seat using keyword 'booked_seats' eg obj.booked_seat
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='bookings')  # seat can access booked_seat using keyword 'booked_seats' eg obj.booked_seat

    class Meta:
        db_table = 'booked_seats'
        unique_together = ['booking', 'seat']

    def __str__(self):
        return f"Booked Seat {self.seat_id.seat_number} for Booking {self.booking_id.id}"
    
# class ShowSeatPrice(models.Model): #to select  price per seat type for a show
#     show = models.ForeignKey(Show, on_delete=models.CASCADE)
#     seat_type = models.CharField(max_length=10, choices=[('regular', 'Regular'), ('vip', 'VIP')])
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.show.id} - {self.seat_type} - {self.price}"
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews",null=False)  # ForeignKey to the user model
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')  # movie can access review using keyword 'reviews' eg obj.review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    ) # Rating out of 5
    comment = models.TextField(null=True, blank=True)  # Optional field for review comment
    review_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ['user', 'movie']  # One review per user per movie
        indexes = [
            models.Index(fields=['movie', 'review_date']),  # For movie reviews
        ]

    def __str__(self):
        return f"Review by User {self.user_id} for Movie {self.movie_id.name}"