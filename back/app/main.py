from fastapi import FastAPI
from dotenv import load_dotenv
import os
import requests
from langchain_openai import OpenAI # OpenAIをインポート
from langchain.prompts import PromptTemplate

# 環境変数の読み込み
load_dotenv()

# 必要な環境変数を .env ファイルから読み込む
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", OPENAI_API_KEY)

# OpenAIのインスタンスを作成
llm = OpenAI(temperature=0.9, api_key=os.getenv("OPENAI_API_KEY"))

# 本当はベクターDBとか PDF などから動的に取得するべき。
knowledge = """
 
"""

app = FastAPI()

@app.get("/places/")
def get_places(location: str = "35.7356,139.6522", query: str = "公園", radius: int = 2000, language: str = "ja"):
    api_key = GOOGLE_MAPS_API_KEY  # APIキーをここに入力してください
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "location": location,
        "query": query,
        "radius": radius,
        "language": language,
        "key": api_key
    }
    
    # Google Places APIを叩く
    response = requests.get(base_url, params=params)
    print("API Response:", response.text)  # 取得したデータを出力

    places_data = response.json()

   # 取得した場所の名前のリストを作る
    places_names = [place['name'] for place in places_data.get('results', [])]

    # レスポンスにOpenAIを利用して加工を行う
    knowledge = f"以下の場所が見つかりました：{', '.join(places_names)}"
    prompt = PromptTemplate(
        input_variables=["knowledge"],
        template=f"""
        {knowledge}

        光が丘に住む30代女性、子供がいて、遠くまでは歩けないが土日に子供と出かけたい。休日の適切な過ごし方を提案してください
        """,
    )

    # OpenAIにプロンプトを送り、レスポンスを得る
    res = llm(prompt.format(knowledge=knowledge))
    return res





# def get_geocode(location: str) -> dict:
#     api_key = os.getenv("GOOGLE_MAPS_API_KEY")
#     params = {
#         'address': location,
#         'key': api_key
#     }
#     response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=params)
#     if response.status_code == 200:
#         json = response.json()
#         if json['results']:
#             return json['results'][0]['geometry']['location']
#     return None

# @app.get("/geocode")
# def read_geocode(location: str = "光が丘駅"):
#     # クエリパラメータとしてlocationを受け取る
#     geocode_info = get_geocode(location)
#     if geocode_info:
#         return geocode_info
#     else:
#         return {"error": "Location not found or API error occurred."}