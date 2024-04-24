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
# from fastapi.security import HTTPBearer
from typing import List
import random #4/11ゆか
import logging
import requests
import httpx
import stripe #stripeをインポート
# import asyncpg
# from .my_prisma import save_recommendation

# 環境変数の読み込み
load_dotenv()

app = FastAPI()
router = APIRouter()
# security = HTTPBearer()

# @app.middleware("http")
# async def csrf_middleware(request: Request, call_next):
#     csrf_token = request.headers.get("X-CSRF-Token")
#     if not csrf_token:
#         raise HTTPException(status_code=400, detail="CSRF token missing")
#     response = await call_next(request)
#     return response

# 必要な環境変数を .env ファイルから読み込む
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", OPENAI_API_KEY)
stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = stripe_secret_key
# DATABASE_URL = os.getenv("DATABASE_URL")

# データベース接続の初期化
# conn: asyncpg.Connection = None

# ロギングの設定
# logging.basicConfig(filename='/logs/app.log', level=logging.DEBUG) # ファイルに出力
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

# @app.on_event("startup")
# async def startup_event():
#     global conn
#     conn = await asyncpg.connect(DATABASE_URL)

# @app.on_event("shutdown")
# async def shutdown_event():
#     global conn
#     await conn.close() 

# @app.get("/csrf-token")
# def get_csrf_token(request: Request):
#     return {"csrf_token": request.session.get("csrf_token")}   

# @app.post("/webhook")
# async def stripe_webhook(request: Request):
#     payload = await request.body()
#     sig_header = request.headers['stripe-signature']
#     endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid payload")
#     except stripe.error.SignatureVerificationError:
#         raise HTTPException(status_code=400, detail="Invalid signature")
    
#     # イベント処理
#     if event['type'] == 'customer.subscription.updated':
#         subscription = event['data']['object']
#         await handle_subscription_update(subscription)

#     return JSONResponse({'status': 'success'})

# async def handle_subscription_update(subscription):
#     query = """
#     INSERT INTO subscriptions (stripe_id, customer_id, status, created_at, updated_at)
#     VALUES ($1, $2, $3, NOW(), NOW())
#     ON CONFLICT (stripe_id) DO UPDATE
#     SET
#         customer_id = EXCLUDED.customer_id,
#         status = EXCLUDED.status,
#         updated_at = NOW();
#     """
#     await conn.execute(

#         query,
#         subscription['id'],  # stripe_id
#         subscription['customer'],  # customer_id
#         subscription['status']  # subscription status
#     )

# @app.get("/user-status/{user_id}")
# async def get_user_status(user_id: int):
#     query = "SELECT status FROM users WHERE id = $1"
#     row = await conn.fetchrow(query, user_id)
#     if row:
#         return {'status': row['status']}
#     else:
#         raise HTTPException(status_code=404, detail="User not found")


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

# class RecommendationModel(BaseModel):
#     user_id: int = Field(..., description="ユーザーの識別ID")
#     company: str = Field(..., description="訪問タイプ")
#     activity_type: str = Field(..., description="どのように時間を過ごすか")
#     recommend_station: str = Field(..., description="推薦された駅の名前")
#     # recommend_details: str = Field(..., description="推薦の詳細情報")

# ------ランダムに取得した駅の名前を基にAPIが周辺情報を取得しLLMに投げその結果を返す------
@app.post("/places/")
async def get_places(query: PlaceQuery):
    logging.debug(f"/place/データを含むリクエストを受信しました: {query.dict()}")
    try:
        # Stripeの顧客IDを取得
        # stripe_customer_id = query.stripe_customer_id

        # Stripeの顧客情報を取得
        # customer = stripe.Customer.retrieve(stripe_customer_id)

        # 顧客のサブスクリプションを確認
        # subscriptions = stripe.Subscription.list(customer=stripe_customer_id, status='active')

        # if not subscriptions.data:
            # サブスクリプションがない場合、制限付きのレスポンスを返す
            # limited_response = ResponseModel(message=llm_response[:100] + "...")
            # return limited_response

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

        # 推薦情報を作成しデータベースに保存 <--- 新たに追加した部分
        # recommendation = RecommendationModel(
        #     user_id=1,
        #     company=query.visit_type,
        #     activity_type=query.how_to_spend_time,
        #     recommend_station=query.station_name,
        #     recommend_details=response.message
        #     )
        # await save_recommendation(recommendation)

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

# Hotpepper APIからレストラン情報を取得してLLMが返す
# @app.get("/recommendations/")
# async def get_recommendations():
#     restaurants = get_hotpepper_data()  # hotpepper.py で定義された関数を呼び出す

#     knowledge = f"以下の場所が見つかりました：{','.join(restaurants)}"
#     prompt = PromptTemplate(
#         input_variables=["knowledge"],
#         template=f"""
#         {knowledge}

#         光が丘に住む30代女性、5歳の子供がいて、おすすめの飲食店を教えて。
#         """,
#     )

#     # OpenAIにプロンプトを送り、JSON形式でレスポンスを得る　4/10 えりな
#     llm_response = llm(prompt.format(knowledge=knowledge), max_tokens=1024) 
#     response = ResponseModel(message=llm_response)
#     return response

##下記マージする方法
# class CombinedResponseModel(BaseModel):
#     places_message: str
#     recommendations_message: str

# @app.get("/combined/", response_model=CombinedResponseModel)
# async def get_combined(location: str = "35.7356,139.6522"):
#     # /places/ からのデータを非同期に取得
#     places_response = await get_places(location=location)
    
#     # /recommendations/ からのデータを非同期に取得
#     # 非同期でデータを取得するためには、get_hotpepper_data 関数も非同期に対応させる必要があります。
#     recommendations_response = await get_recommendations()

#     # 取得したデータをマージ
#     combined_response = CombinedResponseModel(
#         places_message=places_response.message,
#         recommendations_message=recommendations_response.message
#     )

#     return combined_response


# class StationRequest(BaseModel):
#     station_name: str

# app.include_router(router)


# def get_station_by_address(address: str):
#     return find_station(address)
         
#-----位置情報4/11（不特定多数）-----
@app.get("/nearest-station/", response_model=GeocodeResponse)
async def nearest_station_endpoint(address: str):
    return find_nearest_station(address)

#-----練馬駅オンりー検索のみ-----#
# @app.get("/nearest-station/", response_model=GeocodeResponse)
# async def nearest_station_endpoint(address: str):
#     if "練馬駅" in address:
#         return find_nearest_station(address)
#     else:
#         raise HTTPException(status_code=400, detail="このサービスは練馬駅限定です")

# # -----最寄り駅からランダムに周辺の駅を取得-----#
# @app.get("/find-station/")
# def get_station_by_address(address: str):
#     return find_station(address)

# class StationRequest(BaseModel):
#     station_name: str

# app.include_router(router)


# # -----"/stations/"のPOST：使用しなければ消す-----#
# @app.post("/stations/", response_model=StationResponse)
# async def get_station_by_address(request: StationRequest):
#     logger.debug(f"リクエストを受信しました: {request}")
#     try:
#         # 駅の位置情報を取得する非同期関数を呼び出す
#         geocode_response = await find_station_async(request.station_name + "駅")
#         logger.debug(f"Geocode のレスポンスは {request.station_name}: {geocode_response}")

#         # 駅の情報をレスポンスに設定
#         return StationResponse(
#             random_station=geocode_response.nearest_station,
#             nearby_info=[station["name"] for station in geocode_response.nearby_stations]
#         )

#     except Exception as e:
#         logger.error(f"/stations/ エンドポイントのエラー: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))



# --POST検証のため一時的に/places/のGET消しています　4/11のりぴ--使わなければ消す！！4/13
# エンドポイント/placesとどちらでもいいが統一する
# @app.get("/places/")
# async def get_places(location: str = "35.7356,139.6522", query: str = "公園", radius: int = 2000, language: str = "ja"):
#     api_key = GOOGLE_MAPS_API_KEY  # APIキーをここに入力してください
#     google_places_api_endpoint = os.getenv("GOOGLE_PLACES_API_ENDPOINT") # 環境変数からGoogle Places APIエンドポイントを取得
#     params = {
#         "location": location,
#         "query": query,
#         "radius": radius,
#         "language": language,
#         "key": api_key
#     }
    
    # Google Places APIを叩く
    # response = requests.get(google_places_api_endpoint, params=params)
    # print("API Response:", response.text)  # 取得したデータを出力

    # places_data = response.json()

   # 取得した場所の名前のリストを作る　places_namesがリスト
    # places_names = [place['name'] for place in places_data.get('results', [])]

    # レスポンスにOpenAIを利用して加工を行う　取得データをLLMに投げている部分
    # places_namesを文字列に変換しknowledge 変数に格納しプロンプトの一部としてLangChain LLMに送る
    # knowledge = f"以下の場所が見つかりました：{', '.join(places_names)}"
    # prompt = PromptTemplate(
    #     input_variables=["knowledge"],
    #     template=f"""
    #     {knowledge}

    #     光が丘に住む30代女性、５歳の子供がいて、遠くまでは行けないが土日に子供と出かけたい。休日の適切な過ごし方を具体的な場所の名称も用いて提案してください。
    #     """,
    # )

    # OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
    # 文字数増やすコード追加
    # llm_response = llm(prompt.format(knowledge=knowledge), max_tokens=1500)

    # LLMのレスポンスをResponseModelの形式に合わせて整形 JSONに直す
    # response = ResponseModel(message=llm_response)
    # return response

    # こっちはtextになる OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
    # res = llm(prompt.format(knowledge=knowledge))
    # return res