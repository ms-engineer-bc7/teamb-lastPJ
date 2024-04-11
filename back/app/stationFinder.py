from fastapi import FastAPI,HTTPException
import os
from pydantic import BaseModel
from typing import List
import requests
import random  # ランダムに駅を選ぶために追加

app = FastAPI()
# 環境変数からGoogle Maps APIキーを取得
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

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
    nearest_station: str
    nearby_stations: List[str]  # 周辺の駅のリストを含めるために追加


def find_station(address: str) -> GeocodeResponse:
    try:
        # 住所から緯度経度を取得
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
        geocode_response = requests.get(geocode_url)
        geocode_data = geocode_response.json()

        if geocode_data["status"] != "OK":
            raise HTTPException(status_code=404, detail="Address not found")

        latitude = geocode_data["results"][0]["geometry"]["location"]["lat"]
        longitude = geocode_data["results"][0]["geometry"]["location"]["lng"]
        formatted_address = geocode_data["results"][0]["formatted_address"]

        # 周辺の駅を検索
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1500&type=train_station&key={GOOGLE_MAPS_API_KEY}"
        places_response = requests.get(places_url)
        places_data = places_response.json()

        nearby_stations = [station["name"] for station in places_data["results"]]

        # 最も近い駅を設定（リストの最初の要素）
        nearest_station = nearby_stations[0] if nearby_stations else "Nearest station not found"

        # 最も近い駅を除外してから、残りの駅からランダムに1つ選択
        if len(nearby_stations) > 1:
            selected_station = random.choice(nearby_stations[1:])  # 最初の要素をスキップ
        else:
            selected_station = "No additional stations found"

        return GeocodeResponse(
            address_components=[AddressComponent(long_name=address, short_name=address, types=["premise"])],
            formatted_address=formatted_address,
            geometry=Geometry(location=Location(lat=latitude, lng=longitude)),
            nearest_station=nearest_station,  # 最も近い駅
            nearby_stations=[selected_station]  # ランダムに選択された駅をリストとして返す
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from exc
