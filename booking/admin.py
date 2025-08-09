from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from django.utils.html import format_html
from .models import User, Theater, Screen, Movie, Booking, Seat, BookedSeat, Review, Show

print("Booking admin.py loaded")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields shown in list view
    list_display = ('email', 'name', 'role', 'is_staff', 'is_active')
    search_fields = ('email', 'name')
    list_filter = ('role', 'is_staff', 'is_active')

    # Fields shown when viewing/editing a user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    # Fields shown when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role'),
        }),
    )
    ordering = ('-created_at',) #ordred by latest users created on top

class ScreenInline(admin.TabularInline):
    """
    Inline admin for screens within theater admin.
    """
    model = Screen
    extra = 1

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    """
    Theater admin with inline screens management.
    """
    list_display = ('name', 'city', 'location', 'total_screens', 'actual_screens_count')
    list_filter = ('city',)
    search_fields = ('name', 'city')
    inlines = [ScreenInline]
    
    def actual_screens_count(self, obj):
        return obj.screens.count()
    actual_screens_count.short_description = 'Actual Screens'

class SeatInline(admin.TabularInline):
    """
    Inline admin for seats within screen admin.
    """
    model = Seat
    extra = 0
    readonly_fields = ('seat_number',)

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    """
    Screen admin with seat management.
    """
    list_display = ('theater', 'screen_number', 'total_seats')
    list_filter = ('theater', 'theater__city')
    search_fields = ('theater__name', 'screen_number')
    inlines = [SeatInline]
    
    def total_seats(self, obj):
        return obj.seats.count()
    total_seats.short_description = 'Total Seats'

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    """
    Seat admin for individual seat management.
    """
    list_display = ('screen', 'seat_number')
    list_filter = ('screen__theater',)
    search_fields = ('seat_number', 'screen__theater__name')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Movie admin with rich display and filtering options.
    """
    list_display = ('name', 'genre', 'language', 'duration', 'release_date', 'average_rating', 'total_reviews')
    list_filter = ('genre', 'language', 'release_date', 'genre')
    search_fields = ('name', 'description')
    date_hierarchy = 'release_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'poster')
        }),
        ('Movie Details', {
            'fields': ('duration', 'genre', 'language', 'release_date')
        }),
    )

    def average_rating(self, obj):
        avg = obj.average_rating
        if avg > 0:
            return f"{avg:.1f}/10.0"
        return "No ratings"
    average_rating.short_description = 'Avg Rating'


class BookedSeatInline(admin.TabularInline):
    """
    Inline admin for booked seats within booking admin.
    """
    model = BookedSeat
    extra = 0
    readonly_fields = ('seat',)


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    """
    Show admin with booking statistics.
    """
    list_display = ('movie', 'screen', 'show_time', 'price_per_seat', 'occupancy_rate')
    list_filter = ('show_time', 'screen__theater', 'movie__genre')
    search_fields = ('movie__title', 'screen__theater__name')
    date_hierarchy = 'show_time'
    
    def occupancy_rate(self, obj):
        if obj.total_seats > 0:
            rate = (obj.booked_seats_count / obj.total_seats) * 100
            color = 'green' if rate > 70 else 'orange' if rate > 40 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, rate
            )
        return "0%"
    occupancy_rate.short_description = 'Occupancy'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Booking admin with detailed booking information.
    """
    list_display = ('id', 'user', 'show', 'total_price', 'booking_time', 'status', 'seats_count')
    list_filter = ('status', 'booking_time', 'show__movie')
    search_fields = ('user__username', 'user__email', 'show__movie__name')
    date_hierarchy = 'booking_time'
    inlines = [BookedSeatInline]
    
    def seats_count(self, obj):
        return obj.booked_seats.count()
    seats_count.short_description = 'Seats'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Review admin for managing user reviews and ratings.
    """
    list_display = ('user', 'movie', 'rating', 'review_date', 'has_review_text')
    list_filter = ('rating', 'review_date', 'movie__genre')
    search_fields = ('user__username', 'movie__name', 'review_text')
    date_hierarchy = 'review_date'
    
    def has_review_text(self, obj):
        return bool(obj.review_text)
    has_review_text.boolean = True
    has_review_text.short_description = 'Has Review'

