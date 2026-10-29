import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .geofence_engine import GeoFenceAuditor, Coordinate
from .emergency_dispatch import route_to_nearest_station

app = FastAPI(
    title="Guardian Global: Tourist Safety Ingress API",
    description="SIH 2025 Smart Tourist Safety Platform API",
    version="1.0.0"
)

# Load sample zones
with open("data/sample_zones.json") as f:
    ZONES_DATA = json.load(f)

auditor = GeoFenceAuditor(ZONES_DATA["zones"])

class TelemetryPayload(BaseModel):
    tourist_id: str
    lat: float
    lon: float
    alt: Optional[float] = 0.0
    prev_lat: Optional[float] = None
    prev_lon: Optional[float] = None
    prev_timestamp: Optional[float] = None

class SOSPayload(BaseModel):
    tourist_id: str
    lat: float
    lon: float
    incident_type: str = "MANUAL_SOS"

@app.get("/")
def health_check():
    return {
        "system": "Guardian Global Ingress",
        "status": "OPERATIONAL",
        "event": "Smart India Hackathon 2025",
        "timestamp": time.time()
    }

@app.post("/api/v1/geofence/check")
def check_geofence(payload: TelemetryPayload):
    curr = Coordinate(lat=payload.lat, lon=payload.lon, alt=payload.alt, timestamp=time.time())
    prev = None
    if payload.prev_lat and payload.prev_lon and payload.prev_timestamp:
        prev = Coordinate(lat=payload.prev_lat, lon=payload.prev_lon, timestamp=payload.prev_timestamp)

    audit_result = auditor.evaluate_coordinate(curr, prev)
    
    # If breach detected, automatically calculate nearest responder
    dispatch = None
    if audit_result.get("breach"):
        dispatch = route_to_nearest_station(payload.lat, payload.lon, ZONES_DATA["responder_stations"])

    return {
        "tourist_id": payload.tourist_id,
        "audit": audit_result,
        "emergency_dispatch": dispatch
    }

@app.post("/api/v1/emergency/sos")
def trigger_sos(payload: SOSPayload):
    dispatch = route_to_nearest_station(payload.lat, payload.lon, ZONES_DATA["responder_stations"])
    return {
        "ticket_id": f"SOS-{int(time.time())}",
        "status": "DISPATCH_ENGAGED",
        "tourist_id": payload.tourist_id,
        "incident_type": payload.incident_type,
        "dispatch_details": dispatch
    }