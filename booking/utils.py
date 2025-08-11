#helper function to generate random showtimes 
from datetime import time as dtime
import random

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
