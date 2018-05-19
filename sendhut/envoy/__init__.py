"""
order journey: received, in progress, on the way, delivered

Trip fares start with a base amount, then increase with time and distance.

distance between the pickup point and delivery point.
65NGN/KM, which translates to a minimum delivery fee of ₦650

- base fare of 300 NGN (a flat fee that covers the pickup price)
- then increase with time and distance
- dynamic pricing (push vendor commission on to user):
  - traffic, events, weather, timings and driver expertise
  - distance
  - location specific factors
  - demand
  - vehicle type
  - batched delivery or one-off

dispatch to nearest available rider within a certain dispatch radius.
Stays on phone for 7 seconds. If order is not picked, dispatch to the next
nearest available rider if not picked for the same amount of time.
Repeats to all riders within that radius until the order is confirmed.

Lower delivery fees for orders from one of Sendhut partners.

# 2
introduce surge at peak times?

# 3
On top of the delivery fee, charge a convenience fee.
It's a flat fee and amounts to x% of the order.
It factors things like delivery distance and size of order.

A variable percentage-based service fee is also applied to the price
of the items that are ordered


# estimated delivery time
location of the envoy
food preparation time (confirm with restaurants)
amount of traffic
the distance from the pickup location

# multidrop:
Pricing is based on distance, from pickup to drop off, driving down the price per drop.
"""
from django.conf import settings
from geopy.geocoders import GoogleV3

geolocator = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY)
