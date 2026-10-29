"""
Guardian Global: Automated Emergency Responder Dispatch & Triage
Calculates nearest responder outposts and dispatches incidents.
"""

import math
from typing import List, Dict

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

def route_to_nearest_station(tourist_lat: float, tourist_lon: float, stations: List[Dict]) -> Dict:
    closest_station = None
    min_dist = float("inf")

    for st in stations:
        dist = haversine_distance_km(tourist_lat, tourist_lon, st["lat"], st["lon"])
        if dist < min_dist:
            min_dist = dist
            closest_station = st

    return {
        "assigned_station_id": closest_station["id"] if closest_station else None,
        "station_name": closest_station["name"] if closest_station else None,
        "contact": closest_station["contact"] if closest_station else None,
        "estimated_distance_km": round(min_dist, 2),
        "estimated_arrival_minutes": round((min_dist / 25.0) * 60, 1) # Assumes 25 km/h patrol response
    }