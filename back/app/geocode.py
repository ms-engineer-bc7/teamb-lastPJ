from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import os

class AddressComponent(BaseModel):
    long_name: str
    short_name: str
    types: List[str]

class Location(BaseModel):
    lat: float
    lng: float

class Geometry(BaseModel):
    location: Location

class GeocodeResponse(BaseModel):
    address_components: List[AddressComponent]
    formatted_address: str
    geometry: Geometry
    # nearest_station: str  # この行を削除

def find_nearest_station(address: str) -> GeocodeResponse:
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Geocoding API error")

    data = response.json()
    if not data.get("results"):
        raise HTTPException(status_code=404, detail="Address not found")

    result = data["results"][0]
    location = result["geometry"]["location"]
    
    latitude = location["lat"]
    longitude = location["lng"]
    formatted_address = result.get("formatted_address", "")
    address_components = [
        AddressComponent(long_name=component["long_name"], short_name=component["short_name"], types=component["types"]) 
        for component in result["address_components"]
    ]
    geometry = Geometry(location=Location(lat=latitude, lng=longitude))

    # nearest_stationに関連するコードは削除されています

    return GeocodeResponse(
        address_components=address_components,
        formatted_address=formatted_address,
        geometry=geometry,
    )

app = FastAPI()

