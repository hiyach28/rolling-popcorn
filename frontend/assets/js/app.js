// Global variables and state management
let currentUser = null;
let selectedSeats = [];
let currentShow = null;
let currentMovie = null;
let bookingData = {};

// API Base URL
const API_BASE = '/api';

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCSRFToken() {
    return getCookie('csrftoken');
}

// Enhanced API Helper Functions
async function apiCall(endpoint, method = 'GET', data = null, useAuth = true) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (method !== 'GET') {
        headers['X-CSRFToken'] = getCSRFToken();
    }

    if (useAuth && currentUser && currentUser.token) {
        headers['Authorization'] = `Token ${currentUser.token}`;
    }

    const config = {
        method,
        headers,
        credentials: 'include',
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        
        if (response.status === 401) {
            // Clear user data and redirect to login
            currentUser = null;
            localStorage.removeItem('user');
            window.location.href = '/login/';
            return null;
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('API call error:', error);
        showMessage(error.message, 'error');
        return null;
    }
}

// Enhanced Message Display
function showMessage(message, type = 'success', duration = 5000) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-text">${message}</span>
            <button class="message-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, duration);
}

// Enhanced Loading Spinner
function showLoading(message = 'Loading...') {
    hideLoading(); // Remove any existing loading
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-overlay';
    loadingDiv.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    const loadingDiv = document.querySelector('.loading-overlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Authentication functions
async function checkAuthStatus() {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            const response = await apiCall('/auth/profile/', 'GET', null, true);
            if (response && response.id) {
                currentUser = { ...currentUser, ...response };
                localStorage.setItem('user', JSON.stringify(currentUser));
                updateUserMenu();
                return true;
            } else {
                // Invalid token, clear user data
                currentUser = null;
                localStorage.removeItem('user');
            }
        } catch (error) {
            currentUser = null;
            localStorage.removeItem('user');
        }
    }
    updateUserMenu();
    return false;
}

function updateUserMenu() {
    const userMenu = document.querySelector('.user-menu');
    if (!userMenu) return;

    if (currentUser) {
        userMenu.innerHTML = `
            <div class="user-info">
                <div class="user-name">${currentUser.first_name || currentUser.username}</div>
                <div class="user-role">${currentUser.role || 'User'}</div>
            </div>
            <div class="user-actions">
                <a href="/profile/" class="btn btn-sm">Profile</a>
                <button onclick="logout()" class="btn btn-sm btn-danger">Logout</button>
            </div>
        `;
    } else {
        userMenu.innerHTML = `
            <div class="user-info">
                <div class="user-name">Guest</div>
                <div class="user-role">Please Login</div>
            </div>
            <div class="user-actions">
                <a href="/login/" class="btn btn-sm">Login</a>
                <a href="/register/" class="btn btn-sm">Register</a>
            </div>
        `;
    }
}

async function login(email, password) {
    showLoading('Logging in...');
    
    try {
        const response = await apiCall('/auth/login/', 'POST', {
            email: email,
            password: password
        }, false);
        
        if (response && response.token) {
            currentUser = response.user;
            currentUser.token = response.token;
            localStorage.setItem('user', JSON.stringify(currentUser));
            updateUserMenu();
            showMessage('Login successful!', 'success');
            
            // Redirect based on user role
            if (currentUser.role === 'admin') {
                window.location.href = '/dashboard/';
            } else {
                window.location.href = '/';
            }
            return true;
        }
    } catch (error) {
        showMessage('Login failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
    return false;
}

async function register(userData) {
    showLoading('Creating account...');
    
    try {
        const response = await apiCall('/auth/register/', 'POST', userData, false);
        
        if (response && response.token) {
            currentUser = response.user;
            currentUser.token = response.token;
            localStorage.setItem('user', JSON.stringify(currentUser));
            updateUserMenu();
            showMessage('Registration successful!', 'success');
            window.location.href = '/';
            return true;
        }
    } catch (error) {
        showMessage('Registration failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
    return false;
}

async function logout() {
    try {
        await apiCall('/auth/logout/', 'POST');
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        currentUser = null;
        localStorage.removeItem('user');
        updateUserMenu();
        window.location.href = '/';
    }
}

// Enhanced Movie functions
async function loadMovies(filters = {}) {
    showLoading('Loading movies...');
    
    try {
        let endpoint = '/home/';
        const params = new URLSearchParams();
        
        if (filters.search) params.append('search', filters.search);
        if (filters.genres) params.append('genres', filters.genres);
        if (filters.language) params.append('language', filters.language);
        if (filters.theater_city) params.append('theater_city', filters.theater_city);
        if (filters.show_date) params.append('show_date', filters.show_date);
        
        if (params.toString()) {
            endpoint += '?' + params.toString();
        }
        
        const response = await apiCall(endpoint);
        if (response && response.results) {
            displayMovies(response.results);
            return response.results;
        } else if (response) {
            displayMovies(response);
            return response;
        }
    } catch (error) {
        console.error('Error loading movies:', error);
        showMessage('Failed to load movies', 'error');
    } finally {
        hideLoading();
    }
    return [];
}

function displayMovies(movies) {
    const movieGrid = document.querySelector('.movie-grid');
    if (!movieGrid) return;

    if (!movies || movies.length === 0) {
        movieGrid.innerHTML = `
            <div class="no-results">
                <h3>No movies found</h3>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }

    movieGrid.innerHTML = movies.map(movie => `
        <div class="movie-card" onclick="viewMovie(${movie.id})">
            <div class="movie-poster-container">
                <img src="${movie.poster_url || '/frontend/assets/default-movie.jpg'}" 
                     alt="${movie.title || movie.name}" 
                     class="movie-poster"
                     onerror="this.src='/frontend/assets/default-movie.jpg'">
                <div class="movie-overlay">
                    <button class="btn btn-primary">View Details</button>
                </div>
            </div>
            <div class="movie-info">
                <h3 class="movie-title">${movie.title || movie.name}</h3>
                <div class="movie-meta">
                    <span class="movie-language">${movie.language || 'N/A'}</span>
                    <div class="movie-rating">
                        ⭐ ${movie.average_rating ? movie.average_rating.toFixed(1) : 'N/A'}
                    </div>
                </div>
                <div class="movie-genres">
                    ${movie.genres ? movie.genres.map(genre => 
                        `<span class="genre-tag">${genre.name || genre}</span>`
                    ).join('') : ''}
                </div>
                <div class="movie-duration">
                    ${movie.duration ? `${movie.duration} min` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

async function viewMovie(movieId) {
    showLoading('Loading movie details...');
    
    try {
        const movie = await apiCall(`/movies/${movieId}/`);
        if (movie) {
            currentMovie = movie;
            window.location.href = `/movie/${movieId}/`;
        }
    } catch (error) {
        console.error('Error loading movie:', error);
        showMessage('Failed to load movie details', 'error');
    } finally {
        hideLoading();
    }
}

async function loadMovieDetails(movieId) {
    showLoading('Loading movie details...');
    
    try {
        const movie = await apiCall(`/movies/${movieId}/`);
        if (movie) {
            currentMovie = movie;
            displayMovieDetails(movie);
            await loadMovieShows(movieId);
            await loadMovieReviews(movieId);
        }
    } catch (error) {
        console.error('Error loading movie details:', error);
        showMessage('Failed to load movie details', 'error');
    } finally {
        hideLoading();
    }
}

function displayMovieDetails(movie) {
    const movieDetailContainer = document.querySelector('.movie-detail');
    if (!movieDetailContainer) return;

    movieDetailContainer.innerHTML = `
        <div class="movie-poster-section">
            <img src="${movie.poster_url || '/frontend/assets/default-movie.jpg'}" 
                 alt="${movie.title || movie.name}" 
                 class="movie-poster-large"
                 onerror="this.src='/frontend/assets/default-movie.jpg'">
        </div>
        <div class="movie-info-section">
            <h1 class="movie-title-large">${movie.title || movie.name}</h1>
            <div class="movie-meta-large">
                <span class="movie-language">${movie.language || 'N/A'}</span>
                <span class="movie-duration">${movie.duration ? `${movie.duration} min` : ''}</span>
                <span class="movie-rating-large">⭐ ${movie.average_rating ? movie.average_rating.toFixed(1) : 'N/A'}</span>
            </div>
            <div class="movie-genres-large">
                ${movie.genres ? movie.genres.map(genre => 
                    `<span class="genre-tag">${genre.name || genre}</span>`
                ).join('') : ''}
            </div>
            <div class="movie-description">
                <h3>Synopsis</h3>
                <p>${movie.description || 'No description available.'}</p>
            </div>
            <div class="movie-cast">
                <h3>Cast</h3>
                <p>${movie.cast || 'Cast information not available.'}</p>
            </div>
            <div class="movie-director">
                <h3>Director</h3>
                <p>${movie.director || 'Director information not available.'}</p>
            </div>
        </div>
    `;
}

// Show functions
async function loadMovieShows(movieId, filters = {}) {
    try {
        let endpoint = '/shows/';
        const params = new URLSearchParams();
        
        params.append('movie', movieId);
        if (filters.theater_city) params.append('theater_city', filters.theater_city);
        if (filters.show_date) params.append('show_date', filters.show_date);
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        
        endpoint += '?' + params.toString();
        
        const shows = await apiCall(endpoint);
        if (shows) {
            displayShows(shows);
            return shows;
        }
    } catch (error) {
        console.error('Error loading shows:', error);
        showMessage('Failed to load shows', 'error');
    }
    return [];
}

function displayShows(shows) {
    const showsContainer = document.querySelector('.shows-grid');
    if (!showsContainer) return;

    if (!shows || shows.length === 0) {
        showsContainer.innerHTML = `
            <div class="no-shows">
                <h3>No shows available</h3>
                <p>Check back later for show times</p>
            </div>
        `;
        return;
    }

    showsContainer.innerHTML = shows.map(show => `
        <div class="show-card" onclick="selectShow(${show.id})">
            <div class="show-time">${formatShowTime(show.show_time)}</div>
            <div class="show-theater">${show.screen.theater.name}</div>
            <div class="show-screen">Screen ${show.screen.screen_number}</div>
            <div class="show-price">₹${show.price_per_seat}</div>
            <div class="show-availability">
                ${show.available_seats || 0} seats available
            </div>
            <button class="btn btn-primary">Book Now</button>
        </div>
    `).join('');
}

function formatShowTime(showTime) {
    const date = new Date(showTime);
    return date.toLocaleString('en-IN', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function selectShow(showId) {
    showLoading('Loading show details...');
    
    try {
        const show = await apiCall(`/shows/${showId}/`);
        if (show) {
            currentShow = show;
            bookingData.show = show;
            window.location.href = `/seat/?show=${showId}`;
        }
    } catch (error) {
        console.error('Error loading show:', error);
        showMessage('Failed to load show details', 'error');
    } finally {
        hideLoading();
    }
}

// Seat selection functions
async function loadSeatLayout(showId) {
    showLoading('Loading seat layout...');
    
    try {
        const show = await apiCall(`/shows/${showId}/`);
        if (show) {
            currentShow = show;
            displaySeatLayout(show);
        }
    } catch (error) {
        console.error('Error loading seat layout:', error);
        showMessage('Failed to load seat layout', 'error');
    } finally {
        hideLoading();
    }
}

function displaySeatLayout(show) {
    const seatContainer = document.querySelector('.seats-container');
    if (!seatContainer) return;

    const screen = show.screen;
    const seats = screen.seats || [];
    const bookedSeats = show.booked_seats || [];
    
    // Group seats by row
    const seatRows = {};
    seats.forEach(seat => {
        const row = seat.seat_number.match(/^[A-Z]+/)[0];
        if (!seatRows[row]) seatRows[row] = [];
        seatRows[row].push(seat);
    });

    let seatHTML = `
        <div class="screen">SCREEN</div>
        <div class="seat-rows">
    `;

    Object.keys(seatRows).sort().forEach(row => {
        seatHTML += `<div class="seat-row">`;
        seatRows[row].sort((a, b) => {
            const aNum = parseInt(a.seat_number.replace(/[A-Z]/g, ''));
            const bNum = parseInt(b.seat_number.replace(/[A-Z]/g, ''));
            return aNum - bNum;
        }).forEach(seat => {
            const isBooked = bookedSeats.some(booked => booked.seat.id === seat.id);
            const isSelected = selectedSeats.some(selected => selected.id === seat.id);
            
            seatHTML += `
                <div class="seat ${isBooked ? 'booked' : ''} ${isSelected ? 'selected' : ''}" 
                     onclick="${!isBooked ? `toggleSeat(${seat.id}, '${seat.seat_number}')` : ''}"
                     data-seat-id="${seat.id}"
                     data-seat-number="${seat.seat_number}">
                    ${seat.seat_number}
                </div>
            `;
        });
        seatHTML += `</div>`;
    });

    seatHTML += `
        </div>
        <div class="seat-legend">
            <div class="legend-item">
                <div class="legend-seat available"></div>
                <span>Available</span>
            </div>
            <div class="legend-item">
                <div class="legend-seat selected"></div>
                <span>Selected</span>
            </div>
            <div class="legend-item">
                <div class="legend-seat booked"></div>
                <span>Booked</span>
            </div>
        </div>
    `;

    seatContainer.innerHTML = seatHTML;
    updateBookingSummary();
}

function toggleSeat(seatId, seatNumber) {
    const seatElement = document.querySelector(`[data-seat-id="${seatId}"]`);
    const seatIndex = selectedSeats.findIndex(seat => seat.id === seatId);
    
    if (seatIndex > -1) {
        // Remove seat
        selectedSeats.splice(seatIndex, 1);
        seatElement.classList.remove('selected');
    } else {
        // Add seat
        selectedSeats.push({ id: seatId, seat_number: seatNumber });
        seatElement.classList.add('selected');
    }
    
    updateBookingSummary();
}

function updateBookingSummary() {
    const summaryContainer = document.querySelector('.booking-summary');
    if (!summaryContainer || !currentShow) return;

    const totalPrice = selectedSeats.length * currentShow.price_per_seat;
    
    summaryContainer.innerHTML = `
        <h3>Booking Summary</h3>
        <div class="summary-item">
            <span>Movie:</span>
            <span>${currentShow.movie.title || currentShow.movie.name}</span>
        </div>
        <div class="summary-item">
            <span>Theater:</span>
            <span>${currentShow.screen.theater.name}</span>
        </div>
        <div class="summary-item">
            <span>Screen:</span>
            <span>${currentShow.screen.screen_number}</span>
        </div>
        <div class="summary-item">
            <span>Show Time:</span>
            <span>${formatShowTime(currentShow.show_time)}</span>
        </div>
        <div class="summary-item">
            <span>Selected Seats:</span>
            <span>${selectedSeats.map(seat => seat.seat_number).join(', ') || 'None'}</span>
        </div>
        <div class="summary-item">
            <span>Seats:</span>
            <span>${selectedSeats.length}</span>
        </div>
        <div class="summary-item">
            <span>Price per Seat:</span>
            <span>₹${currentShow.price_per_seat}</span>
        </div>
        <div class="summary-item">
            <span>Total Amount:</span>
            <span>₹${totalPrice}</span>
        </div>
        <div class="summary-actions">
            <button class="btn btn-primary" onclick="proceedToPayment()" ${selectedSeats.length === 0 ? 'disabled' : ''}>
                Proceed to Payment
            </button>
        </div>
    `;
}

function proceedToPayment() {
    if (selectedSeats.length === 0) {
        showMessage('Please select at least one seat', 'warning');
        return;
    }
    
    if (!currentUser) {
        showMessage('Please login to continue', 'warning');
        window.location.href = '/login/';
        return;
    }
    
    bookingData.seats = selectedSeats;
    bookingData.totalAmount = selectedSeats.length * currentShow.price_per_seat;
    
    // Store booking data in session storage
    sessionStorage.setItem('bookingData', JSON.stringify(bookingData));
    
    window.location.href = '/payment/';
}

// Review functions
async function loadMovieReviews(movieId) {
    try {
        const reviews = await apiCall(`/movies/${movieId}/reviews/`);
        if (reviews) {
            displayReviews(reviews);
        }
    } catch (error) {
        console.error('Error loading reviews:', error);
    }
}

function displayReviews(reviews) {
    const reviewsContainer = document.querySelector('.reviews-section');
    if (!reviewsContainer) return;

    if (!reviews || reviews.length === 0) {
        reviewsContainer.innerHTML = `
            <h3>Reviews</h3>
            <p>No reviews yet. Be the first to review!</p>
        `;
        return;
    }

    const reviewsHTML = reviews.map(review => `
        <div class="review-item">
            <div class="review-header">
                <div class="review-author">${review.user.username}</div>
                <div class="review-rating">⭐ ${review.rating}</div>
            </div>
            <div class="review-date">${new Date(review.created_at).toLocaleDateString()}</div>
            <div class="review-text">${review.review_text}</div>
        </div>
    `).join('');

    reviewsContainer.innerHTML = `
        <h3>Reviews (${reviews.length})</h3>
        ${reviewsHTML}
        ${currentUser ? `
            <div class="add-review-section">
                <h4>Add Your Review</h4>
                <form onsubmit="submitReview(event, ${movieId})">
                    <div class="form-group">
                        <label>Rating</label>
                        <select class="form-control" id="reviewRating" required>
                            <option value="">Select rating</option>
                            <option value="1">1 ⭐</option>
                            <option value="2">2 ⭐</option>
                            <option value="3">3 ⭐</option>
                            <option value="4">4 ⭐</option>
                            <option value="5">5 ⭐</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Review</label>
                        <textarea class="form-control" id="reviewText" rows="4" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit Review</button>
                </form>
            </div>
        ` : ''}
    `;
}

async function submitReview(event, movieId) {
    event.preventDefault();
    
    const rating = document.getElementById('reviewRating').value;
    const reviewText = document.getElementById('reviewText').value;
    
    if (!rating || !reviewText) {
        showMessage('Please fill in all fields', 'warning');
        return;
    }
    
    try {
        const response = await apiCall('/reviews/create/', 'POST', {
            movie: movieId,
            rating: parseInt(rating),
            review_text: reviewText
        });
        
        if (response) {
            showMessage('Review submitted successfully!', 'success');
            // Reload reviews
            await loadMovieReviews(movieId);
            // Clear form
            document.getElementById('reviewRating').value = '';
            document.getElementById('reviewText').value = '';
        }
    } catch (error) {
        showMessage('Failed to submit review: ' + error.message, 'error');
    }
}

// Payment functions
async function processPayment(paymentData) {
    showLoading('Processing payment...');
    
    try {
        const bookingDataStr = sessionStorage.getItem('bookingData');
        if (!bookingDataStr) {
            throw new Error('No booking data found');
        }
        
        const bookingData = JSON.parse(bookingDataStr);
        
        const response = await apiCall('/bookings/create/', 'POST', {
            show: bookingData.show.id,
            seat_ids: bookingData.seats.map(seat => seat.id),
            payment_method: paymentData.method,
            payment_details: paymentData.details
        });
        
        if (response && response.booking) {
            showMessage('Booking successful!', 'success');
            sessionStorage.removeItem('bookingData');
            window.location.href = `/ticket/?booking=${response.booking.id}`;
            return true;
        }
    } catch (error) {
        showMessage('Payment failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
    return false;
}

// Booking management functions
async function loadUserBookings() {
    showLoading('Loading your bookings...');
    
    try {
        const bookings = await apiCall('/bookings/');
        if (bookings) {
            displayUserBookings(bookings);
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
        showMessage('Failed to load bookings', 'error');
    } finally {
        hideLoading();
    }
}

function displayUserBookings(bookings) {
    const bookingsContainer = document.querySelector('.bookings-container');
    if (!bookingsContainer) return;

    if (!bookings || bookings.length === 0) {
        bookingsContainer.innerHTML = `
            <div class="no-bookings">
                <h3>No bookings found</h3>
                <p>Start by booking a movie ticket!</p>
                <a href="/" class="btn btn-primary">Browse Movies</a>
            </div>
        `;
        return;
    }

    bookingsContainer.innerHTML = bookings.map(booking => `
        <div class="booking-card">
            <div class="booking-header">
                <h3>${booking.show.movie.title || booking.show.movie.name}</h3>
                <span class="booking-status ${booking.status}">${booking.status}</span>
            </div>
            <div class="booking-details">
                <div class="booking-info">
                    <p><strong>Theater:</strong> ${booking.show.screen.theater.name}</p>
                    <p><strong>Screen:</strong> ${booking.show.screen.screen_number}</p>
                    <p><strong>Show Time:</strong> ${formatShowTime(booking.show.show_time)}</p>
                    <p><strong>Seats:</strong> ${booking.booked_seats.map(seat => seat.seat.seat_number).join(', ')}</p>
                    <p><strong>Total Amount:</strong> ₹${booking.total_amount}</p>
                    <p><strong>Booking Date:</strong> ${new Date(booking.booking_time).toLocaleDateString()}</p>
                </div>
                <div class="booking-actions">
                    ${booking.status === 'confirmed' && new Date(booking.show.show_time) > new Date() ? 
                        `<button class="btn btn-danger" onclick="cancelBooking(${booking.id})">Cancel Booking</button>` : 
                        ''
                    }
                    <button class="btn btn-primary" onclick="viewTicket(${booking.id})">View Ticket</button>
                </div>
            </div>
        </div>
    `).join('');
}

async function cancelBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) {
        return;
    }
    
    try {
        const response = await apiCall(`/bookings/${bookingId}/cancel/`, 'POST');
        if (response) {
            showMessage('Booking cancelled successfully', 'success');
            await loadUserBookings();
        }
    } catch (error) {
        showMessage('Failed to cancel booking: ' + error.message, 'error');
    }
}

async function viewTicket(bookingId) {
    window.location.href = `/ticket/?booking=${bookingId}`;
}

// Search and filter functions
function setupSearchAndFilters() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const searchTerm = document.getElementById('searchInput')?.value || '';
            const language = document.getElementById('languageFilter')?.value || '';
            const city = document.getElementById('cityFilter')?.value || '';
            const date = document.getElementById('dateFilter')?.value || '';
            
            const filters = {};
            if (searchTerm) filters.search = searchTerm;
            if (language) filters.language = language;
            if (city) filters.theater_city = city;
            if (date) filters.show_date = date;
            
            loadMovies(filters);
        });
    }
}

// URL parameter utilities
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Initialize app based on current page
async function initApp() {
    await checkAuthStatus();
    
    const currentPage = window.location.pathname;
    
    // Initialize based on current page
    if (currentPage === '/' || currentPage === '/index/') {
        loadMovies();
        setupSearchAndFilters();
    } else if (currentPage.startsWith('/movie/')) {
        const movieId = getUrlParameter('id') || currentPage.split('/')[2];
        if (movieId) {
            await loadMovieDetails(movieId);
        }
    } else if (currentPage === '/shows/') {
        const movieId = getUrlParameter('movie');
        if (movieId) {
            await loadMovieShows(movieId);
        }
    } else if (currentPage === '/seat/') {
        const showId = getUrlParameter('show');
        if (showId) {
            await loadSeatLayout(showId);
        }
    } else if (currentPage === '/booking/') {
        await loadUserBookings();
    } else if (currentPage === '/payment/') {
        // Payment page initialization
        const bookingDataStr = sessionStorage.getItem('bookingData');
        if (!bookingDataStr) {
            window.location.href = '/';
            return;
        }
    } else if (currentPage === '/ticket/') {
        const bookingId = getUrlParameter('booking');
        if (bookingId) {
            await loadTicketDetails(bookingId);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
