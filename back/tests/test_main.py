from fastapi.testclient import TestClient
from app.main import app  # mainモジュールからFastAPIアプリケーションインスタンスをインポートします。

client = TestClient(app)

def test_get_places():
    # 正常なレスポンスをテスト
    response = client.get("/places/")
    assert response.status_code == 200
    assert response.json()["message"]  # 応答の'message'キーが存在することを確認

    # 異常なレスポンスをテスト
    response = client.get("/places/", params={"location": "invalid_location"})
    assert response.status_code == 400  # 不適切なパラメータで400エラーが返されるかをテスト