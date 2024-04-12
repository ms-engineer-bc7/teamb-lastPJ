from fastapi import FastAPI,HTTPException
import os
import httpx  # 非同期HTTPクライアントをインポート
from pydantic import BaseModel
from typing import List
import requests
import random  # ランダムに駅を選ぶために追加
# import logging

app = FastAPI()

# 環境変数からGoogle Maps APIキーを取得
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# ロギング設定
# logging.basicConfig(level=logging.INFO)

class AddressComponent(BaseModel):
    long_name: str
    short_name: str
    types: List[str]

class Location(BaseModel):
    lat: float
    lng: float

class Geometry(BaseModel):
    location: Location

class StationInfo(BaseModel):
    name: str
    location: Location

class GeocodeResponse(BaseModel):
    address_components: List[AddressComponent]
    formatted_address: str
    geometry: Geometry
    nearest_station: str  # 最も近い駅の情報を辞書型で格納
    nearby_stations: List[str]  # 周辺の駅の情報を辞書型のリストで格納

class StationRequest(BaseModel):
    station_name: str  # フロントから送られてくる駅名

class StationResponse(BaseModel):
    random_station: str  # ランダムに選ばれた周辺の駅名
    nearby_info: List[str]  # 選ばれた駅の周辺情報を文字列のリストとして返す

async def find_station_async(address: str) -> GeocodeResponse:
    try:
        async with httpx.AsyncClient() as client:
            # Geocode APIを呼び出し
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
            geocode_response = await client.get(geocode_url)
            if geocode_response.status_code != 200 or geocode_response.json()["status"] != "OK":
                raise HTTPException(status_code=404, detail="住所が見つからないかジオコーディングに失敗しました")
            
            geocode_data = geocode_response.json()
            latitude = geocode_data["results"][0]["geometry"]["location"]["lat"]
            longitude = geocode_data["results"][0]["geometry"]["location"]["lng"]
            formatted_address = geocode_data["results"][0]["formatted_address"]

            places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1500&type=train_station&key={GOOGLE_MAPS_API_KEY}"
            places_response = await client.get(places_url)
            if places_response.status_code != 200 or places_response.json()["status"] != "OK":
                raise HTTPException(status_code=404, detail="近くの駅を取得するのに失敗しました")

            places_data = places_response.json()

            # 駅の名前だけのリストを作成
            station_names = [station["name"] for station in places_data["results"]]
            nearest_station = station_names[0] if station_names else "最寄りの駅が見つかりません"
            nearby_stations = station_names[1:] if len(station_names) > 1 else []

            return GeocodeResponse(
                address_components=[AddressComponent(long_name=address, short_name=address, types=["premise"])],
                formatted_address=formatted_address,
                geometry=Geometry(location=Location(lat=latitude, lng=longitude)),
                nearest_station=nearest_station,
                nearby_stations=nearby_stations
            )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"予期せぬエラーが発生しました: {str(exc)}")