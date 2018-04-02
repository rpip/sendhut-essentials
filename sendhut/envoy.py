"""
distance between the pickup point and delivery point.
65NGN/KM, which translates to a minimum delivery fee of ₦650

- base fare of 300 NGN
- then increase with time and distance
- dynamic pricing:
  -  traffic, events, weather, timings and driver expertise
  - demand
  - vehicle type
  - batched delivery or one-off

dispatch to nearest available rider within a certain dispatch radius.
Stays on phone for 7 seconds. If order is not picked, dispatch to the next
nearest available rider if not picked for the same amount of time.
Repeats to all riders within that radius until the order is confirmed.
"""
from django.conf import settings
from geopy.geocoders import GoogleV3

geolocator = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY)
