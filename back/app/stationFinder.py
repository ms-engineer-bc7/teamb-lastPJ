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

async def find_station(address: str, radius: int = 2000) -> GeocodeResponse:
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





# 日本語にならない
# from fastapi import FastAPI,HTTPException
# import os
# import random  # ランダムに駅を選ぶために追加
# import logging
# import httpx
# from pydantic import BaseModel
# from typing import List, Optional

# app = FastAPI()
# # 環境変数からGoogle Maps APIキーを取得
# GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
# # ロギング設定
# logging.basicConfig(level=logging.INFO)

# class Location(BaseModel):
#     lat: float
#     lng: float

# class StationInfo(BaseModel):
#     name: str
#     location: Location

# class AddressComponent(BaseModel):
#     long_name: str
#     short_name: str
#     types: List[str]    

# class Geometry(BaseModel):
#     location: Location


# # class GeocodeResponse(BaseModel):
# #     address_components: List[Optional[str]] = []
# #     formatted_address: str
# #     geometry: Location
# #     nearest_station: StationInfo # 最も近い駅の情報を辞書型で格納
# #     nearby_stations: List[StationInfo]  # 周辺の駅の情報を辞書型のリストで格納
# #     selected_station: StationInfo  # 追加: ランダムに選択された駅情報全体を返す

# class GeocodeResponse(BaseModel):
#     address_components: List[AddressComponent]
#     formatted_address: str
#     geometry: Geometry
#     nearest_station: StationInfo  # 最も近い駅の情報を辞書型で格納
#     nearby_stations: List[StationInfo]  # 周辺の駅の情報を辞書型のリストで格納
#     selected_station: StationInfo  # 追加: ランダムに選択された駅情報全体を返す

# async def find_station(address: str) -> GeocodeResponse:
#     logging.info(f"検索中の住所: {address}")
#     try:
#         async with httpx.AsyncClient() as client:
#             # 住所から緯度経度を取得（非同期クライアント使用）
#             geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
#             geocode_response = await client.get(geocode_url)
#             geocode_data = geocode_response.json()
#             logging.info(f"Geocode のレスポンス: {geocode_data}")
        
#             if geocode_data["status"] != "OK":
#                logging.error(f"Geocode API call failed: {geocode_response.status_code} - {geocode_response.text}")
#                raise HTTPException(status_code=404, detail="Address not found")

#             latitude = geocode_data["results"][0]["geometry"]["location"]["lat"]
#             longitude = geocode_data["results"][0]["geometry"]["location"]["lng"]
#             formatted_address = geocode_data["results"][0]["formatted_address"]
#             logging.info(f"緯度経度、住所、名前を絞って取得: {formatted_address}")

#             # 上で取得した緯度経度を使用して、周辺の駅を検索
#             places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1700&type=train_station&key={GOOGLE_MAPS_API_KEY}"
#             places_response = await client.get(places_url)
#             places_data = places_response.json()
#             logging.info(f"周辺の駅を検索: {places_data}")

#             if places_data["status"] != "OK":
#                logging.error(f"Places API call failed: {places_response.status_code} - {places_response.text}")
#                raise HTTPException(status_code=404, detail="No stations found")
        
#             #周辺駅名・緯度経度
#             stations = [
#                 StationInfo(
#                     name=station["name"],
#                     location=Location(
#                         lat=station["geometry"]["location"]["lat"],
#                         lng=station["geometry"]["location"]["lng"]
#                     )
#                 ) for station in places_data["results"]
#             ]
        
#             logging.info(f"抽出された駅の名前: {stations}")  # 抽出された駅の名前をログ出力

#             if not stations:
#                 logging.error(f"Places data status error: {places_data.get('status', 'No status')}")
#                 raise HTTPException(status_code=404, detail="No nearby stations")
        

#             # 最も近い駅を設定（リストの最初の要素）
#             nearest_station = stations[0]
#             logging.info(f"最も近い駅の名前: {nearest_station}") 
#             # 最も近い駅以外の駅を選択する
#             selected_station = random.choice([station for station in stations if station != nearest_station]) if len(stations) > 1 else nearest_station
#             logging.info(f"最も近い駅以外の駅の名前: {selected_station}")  # 抽出された駅の名前をログ出力

#             return GeocodeResponse(
#                 address_components=[AddressComponent(long_name=address, short_name=address, types=["premise"])],
#                 formatted_address=formatted_address,
#                 geometry=Geometry(location=Location(lat=latitude, lng=longitude)),
#                 nearest_station=nearest_station,
#                 nearby_stations=stations,
#                 selected_station=selected_station
#             )

#     except HTTPException as http_exc:
#        logging.error(f"HTTPException raised: {http_exc.detail}", exc_info=True)
#        raise http_exc
#     except Exception as exc:
#        logging.error("An unexpected error occurred", exc_info=True)
#        raise HTTPException(status_code=500, detail="An unexpected error occurred") from exc
    







    # class Location(BaseModel):
#     lat: float
#     lng: float

# class StationInfo(BaseModel):
#     name: str
#     location: Location

# class StationResponse(BaseModel):  # このクラスを使用して、フロントエンドに返します。
#     random_station: str
#     latitude: float
#     longitude: float

# class GeocodeResponse(BaseModel):
#     address_components: List[Optional[str]] = []
#     formatted_address: str
#     geometry: Location
#     nearest_station: StationInfo
#     nearby_stations: List[StationInfo]
#     selected_station: StationInfo

# async def find_station(address: str) -> StationResponse:
#     logging.info(f"検索中の住所: {address}")
#     try:
#         async with httpx.AsyncClient() as client:
#             geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
#             geocode_response = await client.get(geocode_url)
#             if geocode_response.status_code != 200 or geocode_response.json().get("status") != "OK":
#                 raise HTTPException(status_code=404, detail="住所が見つかりませんでした")

#             location = geocode_response.json()["results"][0]["geometry"]["location"]
#             places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location['lat']},{location['lng']}&radius=1500&type=train_station&key={GOOGLE_MAPS_API_KEY}"
#             places_response = await client.get(places_url)
#             if places_response.status_code != 200 or places_response.json().get("status") != "OK":
#                 raise HTTPException(status_code=404, detail="駅が見つかりませんでした")

#             stations = [StationInfo(name=place["name"], location=Location(lat=place["geometry"]["location"]["lat"], lng=place["geometry"]["location"]["lng"])) for place in places_response.json()["results"]]

#             if not stations:
#                 raise HTTPException(status_code=404, detail="近くの駅がありません")

#             selected_station = random.choice(stations)

#             return StationResponse(random_station=selected_station.name, latitude=selected_station.location.lat, longitude=selected_station.location.lng)

#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as exc:
#         logging.error("予期せぬエラーが発生しました", exc_info=True)
#         raise HTTPException(status_code=500, detail="サーバー内部でエラーが発生しました") from exc









# class Location(BaseModel):
#     lat: float
#     lng: float

# class StationInfo(BaseModel):
#     name: str
#     location: Location

# class GeocodeResponse(BaseModel):
#     address_components: List[Optional[str]] = []
#     formatted_address: str
#     geometry: Location
#     nearest_station: StationInfo
#     nearby_stations: List[StationInfo]
#     selected_station: StationInfo

# async def find_station(address: str) -> GeocodeResponse:
#     logging.info(f"検索中の住所: {address}")
#     try:
#         async with httpx.AsyncClient() as client:
#             geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
#             geocode_response = await client.get(geocode_url)
#             geocode_data = geocode_response.json()

#             if geocode_data["status"] != "OK":
#                 raise HTTPException(status_code=404, detail="住所が見つかりませんでした")

#             location = geocode_data["results"][0]["geometry"]["location"]
#             formatted_address = geocode_data["results"][0]["formatted_address"]

#             places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location['lat']},{location['lng']}&radius=1500&type=train_station&key={GOOGLE_MAPS_API_KEY}"
#             places_response = await client.get(places_url)
#             places_data = places_response.json()

#             if places_data["status"] != "OK":
#                 raise HTTPException(status_code=404, detail="駅が見つかりませんでした")

#             stations = [StationInfo(name=place["name"], location=Location(lat=place["geometry"]["location"]["lat"], lng=place["geometry"]["location"]["lng"])) for place in places_data["results"]]

#             if not stations:
#                 raise HTTPException(status_code=404, detail="近くの駅がありません")

#             nearest_station = stations[0]
#             selected_station = random.choice([station for station in stations if station.name != address]) if len(stations) > 1 else nearest_station

#             return GeocodeResponse(
#                 formatted_address=formatted_address,
#                 geometry=Location(lat=location['lat'], lng=location['lng']),
#                 nearest_station=nearest_station,
#                 nearby_stations=stations,
#                 selected_station=selected_station
#             )
#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as exc:
#         logging.error("予期せぬエラーが発生しました", exc_info=True)
#         raise HTTPException(status_code=500, detail="サーバー内部でエラーが発生しました") from exc