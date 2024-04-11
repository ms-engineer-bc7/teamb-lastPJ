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

@app.get("/nearest-station/", response_model=GeocodeResponse)
async def nearest_station_endpoint(address: str):
    if "練馬駅" in address:
        return find_nearest_station(address)
    else:
        raise HTTPException(status_code=400, detail="This service is for Nerima Station only.")


#----------エンドポイントに練馬駅指定し全部の情報取得----------#
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List
# import requests
# import os

# class AddressComponent(BaseModel):
#     long_name: str
#     short_name: str
#     types: List[str]

# class Location(BaseModel):
#     lat: float
#     lng: float

# class Geometry(BaseModel):
#     location: Location

# class GeocodeResponse(BaseModel):
#     address_components: List[AddressComponent]
#     formatted_address: str
#     geometry: Geometry
#     nearest_station: str

# def find_nearest_station(address: str) -> GeocodeResponse:
#     # Google Maps APIキーの設定
#     GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    
    
#     # Google Maps Geocoding APIエンドポイント
#     url = "https://maps.googleapis.com/maps/api/geocode/json"
    
#     # リクエストパラメータ
#     params = {
#         "address": address,
#         "key": GOOGLE_MAPS_API_KEY
#     }

#     # APIリクエスト
#     response = requests.get(url, params=params)
#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="Geocoding API error")

#     # APIレスポンスの解析
#     data = response.json()
#     if not data.get("results"):
#         raise HTTPException(status_code=404, detail="Address not found")

#     result = data["results"][0]
#     location = result["geometry"]["location"]
    
#     # 応答データの構築
#     latitude = location["lat"]
#     longitude = location["lng"]
#     formatted_address = result.get("formatted_address", "")
#     address_components = [AddressComponent(long_name=component["long_name"], short_name=component["short_name"], types=component["types"]) for component in result["address_components"]]
#     geometry = Geometry(location=Location(lat=latitude, lng=longitude))
#     nearest_station = "練馬駅"  # この場合、練馬駅を最寄りの駅として返す

#     return GeocodeResponse(
#         address_components=address_components,
#         formatted_address=formatted_address,
#         geometry=geometry,
#         nearest_station=nearest_station
#     )

# app = FastAPI()

# @app.get("/nearest-station/", response_model=GeocodeResponse)
# async def nearest_station_endpoint(address: str):
#     # リクエストの住所が練馬駅かどうかチェック
#     if "練馬駅" in address:
#         return find_nearest_station(address)
#     else:
#         raise HTTPException(status_code=400, detail="This service is for Nerima Station only.")


#----------エンドポイントに住所、施設、駅指定したら住所、緯度経度、近隣駅取得----------#
# from fastapi import HTTPException
# import os
# from pydantic import BaseModel
# from typing import List
# import requests

# # 環境変数からGoogle Maps APIキーを取得
# GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# class AddressComponent(BaseModel):
#     long_name: str
#     short_name: str
#     types: List[str]

# class Location(BaseModel):
#     lat: float
#     lng: float

# class Geometry(BaseModel):
#     location: Location

# class GeocodeResponse(BaseModel):
#     address_components: List[AddressComponent]
#     formatted_address: str
#     geometry: Geometry
#     nearest_station: str

# def find_nearest_station(address: str) -> GeocodeResponse:
#     try:
#         # Google Maps Geocoding APIを使用して住所から緯度経度を取得
#         geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
#         geocode_response = requests.get(geocode_url)
#         geocode_data = geocode_response.json()

#         if geocode_data["status"] != "OK":
#             raise HTTPException(status_code=404, detail="Address not found")

#         # 緯度経度の取得
#         latitude = geocode_data["results"][0]["geometry"]["location"]["lat"]
#         longitude = geocode_data["results"][0]["geometry"]["location"]["lng"]
#         formatted_address = geocode_data["results"][0]["formatted_address"]

#         # Google Places APIを使用して最寄りの駅を検索
#         places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1000&type=train_station&key={GOOGLE_MAPS_API_KEY}"
#         places_response = requests.get(places_url)
#         places_data = places_response.json()

#         if places_data["results"]:
#             nearest_station = places_data["results"][0]["name"]
#         else:
#             nearest_station = "Nearest station not found"

#         # レスポンスを構築
#         return GeocodeResponse(
#             address_components=[AddressComponent(long_name=address, short_name=address, types=["premise"])],
#             formatted_address=formatted_address,
#             geometry=Geometry(location=Location(lat=latitude, lng=longitude)),
#             nearest_station=nearest_station
#         )

#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred") from exc







