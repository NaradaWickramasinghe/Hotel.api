from supabase import create_client, Client
from geopy.distance import geodesic
import math
import os
from dotenv import load_dotenv

load_dotenv()

class HotelService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.table = os.getenv("SUPABASE_TABLE")
        self.supabase: Client = create_client(self.url, self.key)

    def get_hotels(self):
        """Fetch all hotels with their attributes"""
        response = self.supabase.table(self.table).select("*").execute()
        return response.data or []

    def get_booking_counts(self):
        """Fetch all confirmed bookings"""
        response = self.supabase.table("booking").select("hotel_id, booking_status").execute()
        if not response.data:
            return {}
        bookings = {}
        for b in response.data:
            if b["booking_status"] == "Confirmed":
                bookings[b["hotel_id"]] = bookings.get(b["hotel_id"], 0) + 1
        return bookings

    def find_available_hotels(self, latitude, longitude, num_people, limit=5, max_distance_km=10):
        """Find available hotels within 10 km radius, enough rooms for given people"""
        hotels = self.get_hotels()
        bookings = self.get_booking_counts()

        rooms_needed = math.ceil(num_people / 2)
        available_hotels = []

        for hotel in hotels:
            try:
                lat = float(hotel["Latitude"])
                lon = float(hotel["Longitude"])
                distance_km = geodesic((latitude, longitude), (lat, lon)).km
            except Exception:
                continue

            if distance_km > max_distance_km:
                continue

            room_count = hotel.get("room_count", 0)
            booked = bookings.get(hotel["id"], 0)
            available_rooms = room_count - booked

            if available_rooms >= rooms_needed:
                hotel["distance_km"] = round(distance_km, 2)
                available_hotels.append(hotel)

        sorted_hotels = sorted(available_hotels, key=lambda h: h["distance_km"])
        return sorted_hotels[:limit]

    def find_hotels_for_days(self, num_people, daily_locations, limit=5):
        """Return available hotels for each day"""
        results = {}
        for day, location in daily_locations.items():
            lat = location["lat"]
            lon = location["long"]
            results[day] = self.find_available_hotels(lat, lon, num_people, limit)
        return results
