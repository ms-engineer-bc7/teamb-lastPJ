from fastapi import HTTPException
import os
from pydantic import BaseModel
from typing import List, Optional
import httpx
import random
import logging
from dotenv import load_dotenv

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if GOOGLE_MAPS_API_KEY is None:
    raise ValueError("Google Maps API key is not set.")

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)  # デバッグ情報の詳細な出力


class Location(BaseModel):
    lat: float
    lng: float

class StationInfo(BaseModel):
    name: str
    location: Location

class AddressComponent(BaseModel):
    long_name: str
    short_name: str
    types: List[str]

class Geometry(BaseModel):
    location: Location

class GeocodeResponse(BaseModel):
    address_components: List[AddressComponent]
    formatted_address: str
    geometry: Geometry
    nearest_station: Optional[StationInfo]
    nearby_stations: List[StationInfo]

async def find_station(address: str, radius: int = 1750) -> GeocodeResponse:
    async with httpx.AsyncClient() as client:
        try:
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&radius={radius}&language=ja&key={GOOGLE_MAPS_API_KEY}"
            geocode_response = await client.get(geocode_url)
            geocode_data = geocode_response.json()
            
            logging.debug(f"Geocodeのデータ: {geocode_data}")  # データ構造のログ出力

            if geocode_response.status_code != 200 or geocode_data["status"] != "OK":
                raise HTTPException(status_code=404, detail="Address not found")

            latitude = geocode_data["results"][0]["geometry"]["location"]["lat"]
            longitude = geocode_data["results"][0]["geometry"]["location"]["lng"]
            formatted_address = geocode_data["results"][0]["formatted_address"]

            places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&type=train_station&language=ja&key={GOOGLE_MAPS_API_KEY}"
            places_response = await client.get(places_url)
            places_data = places_response.json()
            
            logging.debug(f"周辺の駅情報data: {places_data}")  # 周辺の駅情報のログ出力

            if places_data["status"] != "OK" or not places_data["results"]:
            # if places_response.status_code != 200 or not places_data["results"]:
                raise HTTPException(status_code=404, detail="No nearby stations found")
            stations = [
                StationInfo(name=station["name"], location=Location(lat=station["geometry"]["location"]["lat"], lng=station["geometry"]["location"]["lng"]))
                for station in places_data["results"]
            ]
 
            if not stations:
                raise HTTPException(status_code=404, detail="No stations found")
  
            nearest_station = stations[0] 
            logging.debug(f"最寄り駅: {nearest_station}")  
            other_stations = stations[1:] if len(stations) > 1 else []
            logging.debug(f"最寄り駅以外の駅: {other_stations}")  

            return GeocodeResponse(
                address_components=[AddressComponent(long_name=address, short_name=address, types=["premise"])],
                formatted_address=formatted_address,
                geometry=Geometry(location=Location(lat=latitude, lng=longitude)),
                nearest_station=nearest_station,
                nearby_stations=other_stations
            )
             
        except HTTPException as e:
            logging.error(f"HTTP Error: {e.detail}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
