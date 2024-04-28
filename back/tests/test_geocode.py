from fastapi.testclient import TestClient
from main import app  # main.pyがあなたのFastAPIアプリのファイル名であることを仮定

client = TestClient(app)

def test_geocode_success():
    # 正常系テスト: 適切なアドレスが与えられた場合
    response = client.get("/geocode?address=東京タワー")
    assert response.status_code == 200
    data = response.json()
    assert data['formatted_address'] == '東京タワー'  # 実際の応答に基づいて適切に調整してください
    assert 'lat' in data['geometry']['location']
    assert 'lng' in data['geometry']['location']

def test_geocode_failure():
    # 異常系テスト: 存在しないアドレスが与えられた場合
    response = client.get("/geocode?address=このアドレスは存在しません")
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Address not found'

# さらに、適切なパラメータなしでAPIを呼び出した場合のテストも追加可能です
def test_geocode_no_params():
    # パラメータなしのリクエスト
    response = client.get("/geocode")
    assert response.status_code == 422  # FastAPIのバリデーションエラーは通常422エラーを返します
