from fastapi import APIRouter, HTTPException 
from dotenv import load_dotenv
import requests
import os
import random
import math

load_dotenv(os.path.join(os.path.abspath(os.curdir), ".env"))
API_KEY = os.getenv("HOT_PEPPER_API_KEY")

router = APIRouter()

HOTPEPPER_URL = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
OUTPUT_FORMAT = "json"
RESPONSE_TARGET = "shop"

# 練馬駅の緯度と経度
BASE_LATITUDE = 35.735657
BASE_LONGITUDE = 139.651259
RANGE = "3"

def generate_random_coordinates(lat, lng, radius=1000):
    """
    指定された中心座標と半径(メートル)内でランダムな座標を生成する。
    """
    print("Generating random coordinates...")
    # 地球の半径（メートル）
    earth_radius = 6371000  

    # ランダムな距離と角度
    random_distance = random.uniform(0, radius)
    random_angle = random.uniform(0, 2 * math.pi)
    print(f"Random distance: {random_distance}, Random angle: {random_angle}")

    # ランダムな座標の計算
    delta_lat = random_distance * math.cos(random_angle) / earth_radius
    delta_lng = random_distance * math.sin(random_angle) / (earth_radius * math.cos(math.pi * lat / 180))

    new_lat = lat + (delta_lat * 180 / math.pi)
    new_lng = lng + (delta_lng * 180 / math.pi)
    print(f"Generated coordinates: Latitude = {new_lat}, Longitude = {new_lng}")

    return new_lat, new_lng

@router.get("/hotpepper")
def get_hotpepper_data():
    print("Starting API request for HotPepper data...")
    # ランダムな座標の生成
    lat, lng = generate_random_coordinates(BASE_LATITUDE, BASE_LONGITUDE, 1000)
    print(f"Using coordinates: Latitude = {lat}, Longitude = {lng}")

    params = {
        "key": API_KEY,
        "lat": lat,
        "lng": lng,
        "range": RANGE,
        "format": OUTPUT_FORMAT,
    }
    print(f"Request parameters: {params}")

    
    try:
        response = requests.get(HOTPEPPER_URL, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"APIリクエストに失敗しました: {e}")

    data = response.json()
    print("Received response from API.")

    if "results" not in data or RESPONSE_TARGET not in data["results"]:
        raise HTTPException(status_code=500, detail="APIからの応答が不正です")
    
    # shop_names = [shop['name'] for shop in data["results"][RESPONSE_TARGET]]

    return data
   


