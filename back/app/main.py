from fastapi import FastAPI, HTTPException, APIRouter, Query, Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from langchain_openai import OpenAI # OpenAIをインポート
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field  #PydanticのBaseModel追加　4/9のりぴ　# Fieldをインポート 
from .routes.hotpepper import get_hotpepper_data #horpepperのデータを追加　4/9えりな
from fastapi.middleware.cors import CORSMiddleware #CORS設定 4/10のりぴ
from .routes.directions import router as directions_router #4/11えりな
from .geocode import find_nearest_station, GeocodeResponse #4/11ゆか
from .stationFinder import find_station, GeocodeResponse
from typing import List
import random #4/11ゆか
import logging
import requests
import httpx
import stripe #stripeをインポート

# 環境変数の読み込み
load_dotenv()

app = FastAPI()
router = APIRouter()

# 必要な環境変数を .env ファイルから読み込む
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = stripe_secret_key

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)  #コンソールに出力
logger = logging.getLogger(__name__)

# OpenAIのインスタンスを作成　生成されるテキストの予測可能性 値を下げるとより確定的になる
llm = OpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))

# 本当はベクターDBとか PDF などから動的に取得するべき。
knowledge = """
 
"""

# CORSミドルウェアの設定 4/10のりぴ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

@app.get("/")
def read_root():
    return {"Hello": "BuRaRi-さんぽっと-"}

class ResponseModel(BaseModel):#追加　4/9のりぴ
      message: str

class StationResponse(BaseModel):
    random_station: str  # ランダムに選ばれた駅の名前
    latitude: float # 数値型！ ランダムに選ばれた駅の緯度経度
    longitude: float # 数値型！ ランダムに選ばれた駅の緯度経度
    # japanese_name: str  # 日本語の駅名

# -----最寄り駅からランダムに周辺の駅を取得-----#
@app.get("/find-station/")
async def get_random_station(address: str) -> dict:
    try:
        # find_station関数を呼び出して駅情報を取得
        response = await find_station(address)
        logging.debug(f"find_station関数を呼び出して駅情報を取得: {response}")

        if response.nearby_stations:
           # nearby_stationsからランダムに駅を選択
           random_station = random.choice(response.nearby_stations)
           logging.debug(f"nearby_stationsからランダムに駅を選択: {random_station}")
        
           # 選択されたランダムな駅と位置情報を含む辞書を返す
           station_response = StationResponse(
               random_station=random_station.name,
               latitude=random_station.location.lat,
               longitude=random_station.location.lng
           )
           logging.debug(f"選択されたランダムな駅と位置情報を含む辞書を返す: {station_response}")
        
           return JSONResponse(content=station_response.dict())
     
        else:
            # nearby_stationsが空の場合は最寄り駅の情報を返す
            nearest_station = response.nearest_station
            station_response = StationResponse(
                random_station=nearest_station.name,
                latitude=nearest_station.location.lat,
                longitude=nearest_station.location.lng
            )
            logging.debug(f"最寄り駅の情報を返す: {station_response}")
            
            return JSONResponse(content=station_response.dict())

    except HTTPException as e:
        return {"error": e.detail}

class PlaceQuery(BaseModel):
    language: str = Field(default="ja", example="ja")
    station_name: str = Field(description="ランダムに選ばれた駅名を含む")
    visit_type: str = Field(description="訪問タイプを必須フィールドにする", example="一人")
    radius: int = Field(default=1000, description="検索範囲の半径（メートル）", example=1000)
    latitude: float = Field(description="駅の緯度")
    longitude: float = Field(description="駅の経度")
    how_to_spend_time: str = Field(description="どんな時間を過ごしたいか: のんびりとしたorアクティブなor少しの限られた", example="leisurely")

class ResponseModel(BaseModel):
    message: str

# ------ランダムに取得した駅の名前を基にAPIが周辺情報を取得しLLMに投げその結果を返す------
@app.post("/places/")
async def get_places(query: PlaceQuery):
    logging.debug(f"/place/データを含むリクエストを受信しました: {query.dict()}")
    try:
        # APIリクエスト設定
        google_places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        logging.debug(f"google_places_url: {google_places_url}")
        
        # 追加
        types = [
            "park", 
            "restaurant", 
            "cafe", 
            "amusement_park", 
            "tourist_attraction", 
            "shopping_mall", 
            "spa",
            "movie_theater",
            "aquarium",  # 水族館 (子供向け)
            "zoo",  # 動物園 (子供向け)
            "museum",  # 博物館 (子供向け、大人向け)
            "art_gallery",  # 美術館 (デート向け、おしゃれ)
            "bowling_alley",
            "stadium",  # スタジアム (アクティブ、大人向け)
            "library",  # 図書館 (子供向け、大人向け)
            "shopping_mall",  # ショッピングモール (デート向け、おしゃれ)
            "clothing_store",
            "pet_store",
            "bakery",
            "airport",
            ]
        places_data_results = []

        # ランダムに10件の場所の種類を選択
        random_types = random.sample(types, 10)

        async with httpx.AsyncClient() as client:
            for place_type in random_types:
                params = {
                    'key': GOOGLE_MAPS_API_KEY,
                    'location': f"{query.latitude},{query.longitude}",  # フロントエンドから受け取った緯度経度
                    'radius': query.radius,  # radiusを整数に変更
                    # 追加
                    'type': place_type,
                    'language': query.language,
                }

                logging.debug(f"APIに渡すparamsの内容: {params}")

                # async with httpx.AsyncClient() as client:
                resp = await client.get(google_places_url, params=params)
                logging.debug(f"Google Places API Request URL: {resp.url}")
                logging.debug(f"Google Places API Response Status: {resp.status_code}")

                if resp.status_code != 200:
                   logger.error(f"Google Places APIエラー: {resp.text}")
                   raise HTTPException(status_code=resp.status_code, detail=resp.text)
                   #continue  # エラーがあればログに記録して次のタイプへ
                   # LLMにデータを渡し、処理を行う部分を実装。
                   # ここではGoogle Places APIから得たデータを返す。
                else:
                   places_data = resp.json()
                   logging.debug(f"Google Places APIから得たデータの中身JSON: {places_data}")
                   places_data_results.extend(places_data.get('results', []))     
                   logging.error(f"Google Places APIから得たデータの中身 : {resp.text}")
                    
                # エラークライアントに返す
                # raise HTTPException(status_code=resp.status_code, detail=resp.text)  

        # 取得した場所の名前のリストを作る　places_namesがリスト
        places_names = [place['name'] for place in places_data_results]
        logging.debug(f"Google Places APIから得たデータをリスト化: {places_names}")
        
        # レスポンスにOpenAIを利用して加工を行う　取得データをLLMに投げている部分
        # places_namesを文字列に変換しknowledge 変数に格納しプロンプトの一部としてLangChain LLMに送る
        knowledge = f"以下の場所が見つかりました：{', '.join(places_names)}"
        logging.debug(f"LLM に渡すためにAPIから抽出された内容=knowledge: {knowledge}")
        
        visit_type_description = f"訪問タイプ: {query.visit_type}"
        logging.debug(f"訪問タイプ渡っているか: {visit_type_description}")
        how_to_spend_time_description = f"どんな時間を過ごす？: {query.how_to_spend_time}"
        logging.debug(f"どんな時間を過ごすか: {how_to_spend_time_description}")

        # {knowledge} でリスト化
        prompt = PromptTemplate(
            input_variables=["knowledge", "station_name", "visit_type_description", "how_to_spend_time_description"],
            template=f"""
                土日に{query.station_name}駅周辺の徒歩で行ける範囲に{visit_type_description}外出して
                {how_to_spend_time_description}時間を過ごしたいと考えている。
                最適な、休日の過ごし方を、下記の周辺情報から選び、
                ピックアップした上で行く相手に合わせた場所の提案を３～４パターン提案をして欲しい。
                また、提案する時の口調は、優しい感じで、「休日の過ごし方について提案させていただきますね。まずは～」
                のように話し始めて下さい。
    
                回答は必ず日本語の文章のみで行ってください。
                コードやプログラミング言語、変数、特殊な記号などは絶対に使用しないでください。
                Console.WriteLineなどのコードを含めないでください。
                もし使用した場合は、回答全体を自然な日本語の文章に書き換えてください。
    
                周辺情報: {knowledge}
            """,
        )
        
        # OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
        # 文字数増やすコード追加
        llm_response = llm(prompt.format(knowledge=knowledge), max_tokens=1500)
        logging.info(f"LLMからの応答: {llm_response}")
        # LLMのレスポンスをResponseModelの形式に合わせて整形 JSONに直す
        response = ResponseModel(message=llm_response)

        return response
    
    except Exception as e:
        logging.error(f"/places/ エンドポイントのエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部エラーが発生しました: {str(e)}") 


# directions ルーターを追加 4/11えりな
app.include_router(directions_router)

# 新しいPaymentIntentを作成するエンドポイント
@app.get("/secret")
def create_payment_intent():
    intent = stripe.PaymentIntent.create(
        amount=330, 
        currency="jpy", 
        payment_method_types=["card"],
    )
    return {"client_secret": intent.client_secret}
  
#-----位置情報4/11（不特定多数）-----
@app.get("/nearest-station/", response_model=GeocodeResponse)
async def nearest_station_endpoint(address: str):
    return find_nearest_station(address)

