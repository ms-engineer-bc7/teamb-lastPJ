from fastapi.testclient import TestClient
from app.main import app  # mainモジュールからFastAPIアプリケーションインスタンスをインポートします。
import pytest

client = TestClient(app)

def test_get_places():
    # 正常なレスポンスをテスト
    response = client.get("/places/")
    assert response.status_code == 200
    assert response.json()["message"]  # 応答の'message'キーが存在することを確認

    # 異常なレスポンスをテスト
    response = client.get("/places/", params={"location": "invalid_location"})
    assert response.status_code == 400  # 不適切なパラメータで400エラーが返されるかをテスト
    
def test_find_station():
    response = client.get("/find_station?address=東京駅")
    assert response.status_code == 200
    assert "東京駅" in response.json()['nearest_station']['name']
    
def test_find_station_error():
    # 不正な住所をテスト
    response = client.get("/find_station?address=存在しない住所")
    assert response.status_code == 404  # 404エラーが返されることを確認
    assert "住所が見つかりません" in response.json()['detail']  # エラーメッセージが適切かを確認
