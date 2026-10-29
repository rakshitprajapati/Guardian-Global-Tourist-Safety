"""
Guardian Global: Spatial Geo-Fencing & Spoofing Detection Engine
Engineered for Smart India Hackathon (SIH) 2025
Author: Kolawada Rakshit (System Architect)
"""

import math
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel

class Coordinate(BaseModel):
    lat: float
    lon: float
    alt: Optional[float] = 0.0
    timestamp: Optional[float] = 0.0

class GeoFenceAuditor:
    def __init__(self, zones: List[Dict]):
        self.zones = zones

    @staticmethod
    def is_point_in_polygon(point: Coordinate, polygon: List[Dict]) -> bool:
        """
        Ray-Casting Algorithm to test point-in-polygon containment.
        Computes intersection count of horizontal ray with polygon segments.
        """
        x, y = point.lon, point.lat
        inside = False
        n = len(polygon)

        for i in range(n):
            j = (i + 1) % n
            xi, yi = polygon[i]["lon"], polygon[i]["lat"]
            xj, yj = polygon[j]["lon"], polygon[j]["lat"]

            # Check if point is between horizontal limits of segment
            intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
            if intersect:
                inside = not inside

        return inside

    @staticmethod
    def calculate_velocity_kmh(p1: Coordinate, p2: Coordinate) -> float:
        """
        Calculates speed between two successive telemetry heartbeats.
        Rejects telemetry where tourist travels at physically impossible speeds on foot.
        """
        if p2.timestamp <= p1.timestamp:
            return 0.0

        # Haversine distance in km
        r = 6371.0 # Earth radius
        phi1 = math.radians(p1.lat)
        phi2 = math.radians(p2.lat)
        delta_phi = math.radians(p2.lat - p1.lat)
        delta_lambda = math.radians(p2.lon - p1.lon)

        a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = r * c

        time_hours = (p2.timestamp - p1.timestamp) / 3600.0
        return distance_km / time_hours if time_hours > 0 else 0.0

    def evaluate_coordinate(self, coord: Coordinate, previous_coord: Optional[Coordinate] = None) -> Dict:
        """
        Full audit pipeline: Spoof filter -> Zone containment check -> Alert generation
        """
        # 1. Spoof Check
        if previous_coord and previous_coord.timestamp > 0:
            speed = self.calculate_velocity_kmh(previous_coord, coord)
            if speed > 120.0:  # Faster than 120 km/h in mountain terrain
                return {
                    "status": "REJECTED_SPOOF",
                    "reason": f"Anomalous velocity detected: {speed:.1f} km/h (threshold: 120 km/h)",
                    "breach": False
                }

        # 2. Polygon Check
        for zone in self.zones:
            if self.is_point_in_polygon(coord, zone["polygon"]):
                return {
                    "status": "PERIMETER_BREACH" if zone["type"] == "Restricted" else "IN_SAFE_ZONE",
                    "zone_id": zone["id"],
                    "zone_name": zone["name"],
                    "risk_level": zone["risk_level"],
                    "breach": zone["type"] == "Restricted"
                }

        return {
            "status": "UNMAPPED_TERRAIN",
            "risk_level": "MODERATE",
            "breach": False
        }