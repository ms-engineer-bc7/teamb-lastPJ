from fastapi.testclient import TestClient
from app.main import app  # mainモジュールからFastAPIアプリケーションインスタンスをインポート
import pytest

@pytest.fixture
def client():
    return TestClient(app)

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "BuRaRi-さんぽっと-"}

def test_get_random_station(client):
    # 住所を正しく渡す例
    response = client.get("/find-station/?address=東京駅")
    assert response.status_code == 200
    # 応答から期待する値を確認する具体的なテストを書く
    assert "latitude" in response.json()

def test_get_random_station_error(client):
    # 不正な住所を渡す例
    response = client.get("/find-station/?address=存在しない住所")
    assert response.status_code == 404
    assert "住所が見つかりません" in response.json()['detail']

def test_get_places(client):
    # 正しいリクエストボディを含むPOSTリクエストを送信
    request_data = {
        "language": "ja",
        "station_name": "東京",
        "visit_type": "一人",
        "radius": 1000,
        "latitude": 35.682839,
        "longitude": 139.759455,
        "how_to_spend_time": "leisurely"
    }
    response = client.post("/places/", json=request_data)
    assert response.status_code == 200
    assert "message" in response.json()

# from fastapi.testclient import TestClient
# from app.main import app  # mainモジュールからFastAPIアプリケーションインスタンスをインポートします。
# import pytest

# client = TestClient(app)

# def test_get_places():
#     # 正常なレスポンスをテスト
#     response = client.get("/places/")
#     assert response.status_code == 200
#     assert response.json()["message"]  # 応答の'message'キーが存在することを確認

#     # 異常なレスポンスをテスト
#     response = client.get("/places/", params={"location": "invalid_location"})
#     assert response.status_code == 400  # 不適切なパラメータで400エラーが返されるかをテスト
    
# def test_find_station():
#     response = client.get("/find_station?address=東京駅")
#     assert response.status_code == 200
#     assert "東京駅" in response.json()['nearest_station']['name']
    
# def test_find_station_error():
#     # 不正な住所をテスト
#     response = client.get("/find_station?address=存在しない住所")
#     assert response.status_code == 404  # 404エラーが返されることを確認
#     assert "住所が見つかりません" in response.json()['detail']  # エラーメッセージが適切かを確認
