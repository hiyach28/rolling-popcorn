#helper function to generate random showtimes 
from datetime import time as dtime
import random
from typing import List


def generate_random_showtimes(count, start_hour=10, end_hour=24, min_gap=2):
    """
    Generate 'count' random show start times between start_hour and end_hour
    with at least min_gap hours between shows.
    Returns a sorted list of 'datetime.time' objects.
    """
    all_possible = []
    current = start_hour
    while current + min_gap <= end_hour:
        all_possible.append(current)
        current += min_gap

    chosen = random.sample(all_possible, min(count, len(all_possible)))
    chosen.sort()
    return [dtime(hour=h, minute=0) for h in chosen]



def generate_seat_layout(rows: int, seats_per_row: int, vip_rows: List[int] = None) -> dict:
    """
    Generate a seat layout for a screen.
    
    Args:
        rows: Number of rows in the screen
        seats_per_row: Number of seats per row
        vip_rows: List of row numbers that should be VIP (optional)
    
    Returns:
        Dictionary containing seat layout information
    """
    if vip_rows is None:
        vip_rows = []
    
    layout = {
        'rows': rows,
        'seats_per_row': seats_per_row,
        'total_seats': rows * seats_per_row,
        'vip_rows': vip_rows,
        'seat_map': {}
    }
    
    # Generate seat map
    for row in range(1, rows + 1):
        row_letter = chr(64 + row)  # A, B, C, etc.
        layout['seat_map'][row_letter] = []
        
        for seat in range(1, seats_per_row + 1):
            seat_info = {
                'seat_number': f"{row_letter}{seat}",
                'seat_type': 'vip' if row in vip_rows else 'regular',
                'row': row,
                'position': seat
            }
            layout['seat_map'][row_letter].append(seat_info)
    
    return layout

