import pytest
from httpx import AsyncClient
from main import app  

@pytest.mark.asyncio
async def test_get_directions():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/directions/", params={"origin": "東京駅", "destination": "新宿駅"})
        assert response.status_code == 200
        assert "legs" in response.json()[0]  # 結果に「legs」フィールドが含まれているか確認

@pytest.mark.asyncio
async def test_get_directions_invalid_mode():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/directions/", params={"origin": "東京駅", "destination": "新宿駅", "mode": "flying"})
        assert response.status_code == 400
        assert "error" in response.json()  # エラーメッセージが含まれていることを確認

# 以下の行は、pytestをコマンドラインで直接呼び出したときにのみテストを実行するためのものです。
if __name__ == "__main__":
    pytest.main()
