from fastapi import HTTPException
import pytest
import os
from httpx import Response
from unittest.mock import patch
from stationFinder import find_nearest_station, GOOGLE_MAPS_API_KEY  # find_nearest_station 関数が存在すると仮定

def test_google_maps_api_key():
    assert GOOGLE_MAPS_API_KEY is not None, "Google Maps API key should not be None."

@patch("httpx.get")
def test_find_nearest_station_success(mock_get):
    # 成功したレスポンスのシミュレーション
    mock_get.return_value = Response(status_code=200, json={
        "results": [{
            "formatted_address": "Tokyo Station, Tokyo, Japan",
            "geometry": {
                "location": {
                    "lat": 35.681236,
                    "lng": 139.767125
                }
            }
        }]
    })

    station = find_nearest_station("Tokyo Station")
    assert station == "Tokyo Station, Tokyo, Japan", "Should return the correct formatted address"

@patch("httpx.get")
def test_find_nearest_station_failure(mock_get):
    # 404 エラーのシミュレーション
    mock_get.return_value = Response(status_code=404, json={"error": "Not found"})

    with pytest.raises(HTTPException) as excinfo:
        find_nearest_station("Invalid Location")
    assert excinfo.value.status_code == 404, "Should raise HTTPException with status code 404"

# 環境変数が設定されているかのテスト
def test_google_maps_api_key_set():
    assert os.getenv("GOOGLE_MAPS_API_KEY") is not None, "Environment variable GOOGLE_MAPS_API_KEY should be set"

# APIキーが設定されていない場合のエラーテスト
@patch("os.getenv", return_value=None)
def test_google_maps_api_key_not_set(mock_getenv):
    with pytest.raises(ValueError) as excinfo:
        # 関数内でAPIキーを取得しようとするシミュレーション
        find_nearest_station("Tokyo Station")
    assert "Google Maps API key is not set" in str(excinfo.value), "Should raise ValueError if API key is not set"

