from fastapi import APIRouter
from googlemaps import Client as GoogleMaps
from fastapi.responses import JSONResponse
from typing import Optional
import os

router = APIRouter()

# Google Maps クライアントの設定
gmaps = GoogleMaps(key=os.getenv("GOOGLE_MAPS_API_KEY"))

@router.get("/directions/")
async def get_directions(origin: str, destination: str, mode: Optional[str] = "walking"):
    try:
        directions_result = gmaps.directions(origin, destination, mode=mode)
        return JSONResponse(content=directions_result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
