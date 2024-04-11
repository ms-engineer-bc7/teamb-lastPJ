from fastapi import FastAPI
import os
import stripe #stripeをインポート
from dotenv import load_dotenv
import requests
from langchain_openai import OpenAI # OpenAIをインポート
from langchain.prompts import PromptTemplate
from pydantic import BaseModel #PydanticのBaseModel追加　4/9のりぴ
from .routes.hotpepper import get_hotpepper_data #horpepperのデータを追加　4/9えりな
from fastapi.middleware.cors import CORSMiddleware #CORS設定 4/10のりぴ
from .routes.directions import router as directions_router #4/11えりな


# 環境変数の読み込み
load_dotenv()

# 必要な環境変数を .env ファイルから読み込む
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", OPENAI_API_KEY)
stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = stripe_secret_key
print("Stripe_SECRET_Key:", stripe.api_key) # デバッグ用の行

# OpenAIのインスタンスを作成　生成されるテキストの予測可能性
llm = OpenAI(temperature=0.9, api_key=os.getenv("OPENAI_API_KEY"))

# 本当はベクターDBとか PDF などから動的に取得するべき。
knowledge = """
 
"""

app = FastAPI()

# CORSミドルウェアの設定 4/10のりぴ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

class ResponseModel(BaseModel):#追加　4/9のりぴ
    message: str

# directions ルーターを追加 4/11えりな
app.include_router(directions_router)

# エンドポイント/placesとどちらでもいいが統一する
@app.get("/places/")
async def get_places(location: str = "35.7356,139.6522", query: str = "公園", radius: int = 2000, language: str = "ja"):
    api_key = GOOGLE_MAPS_API_KEY  # APIキーをここに入力してください
    google_places_api_endpoint = os.getenv("GOOGLE_PLACES_API_ENDPOINT") # 環境変数からGoogle Places APIエンドポイントを取得
    params = {
        "location": location,
        "query": query,
        "radius": radius,
        "language": language,
        "key": api_key
    }
    
    # Google Places APIを叩く
    response = requests.get(google_places_api_endpoint, params=params)
    print("API Response:", response.text)  # 取得したデータを出力

    places_data = response.json()

   # 取得した場所の名前のリストを作る　places_namesがリスト
    places_names = [place['name'] for place in places_data.get('results', [])]

    # レスポンスにOpenAIを利用して加工を行う　取得データをLLMに投げている部分
    # places_namesを文字列に変換しknowledge 変数に格納しプロンプトの一部としてLangChain LLMに送る
    knowledge = f"以下の場所が見つかりました：{', '.join(places_names)}"
    prompt = PromptTemplate(
        input_variables=["knowledge"],
        template=f"""
        {knowledge}

        光が丘に住む30代女性、５歳の子供がいて、遠くまでは行けないが土日に子供と出かけたい。休日の適切な過ごし方を具体的な場所の名称も用いて提案してください。
        """,
    )

    # OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
    # 文字数増やすコード追加
    llm_response = llm(prompt.format(knowledge=knowledge), max_tokens=1500)

    # LLMのレスポンスをResponseModelの形式に合わせて整形 JSONに直す
    response = ResponseModel(message=llm_response)
    return response

    # こっちはtextになる OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
    # res = llm(prompt.format(knowledge=knowledge))
    # return res

@app.get("/")
def read_root():
    return {"Hello": "World"}

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
@app.get("/recommendations/")
async def get_recommendations():
    restaurants = get_hotpepper_data()  # hotpepper.py で定義された関数を呼び出す

    knowledge = f"以下の場所が見つかりました：{','.join(restaurants)}"
    prompt = PromptTemplate(
        input_variables=["knowledge"],
        template=f"""
        {knowledge}

        光が丘に住む30代女性、5歳の子供がいて、おすすめの飲食店を教えて。
        """,
    )

    # OpenAIにプロンプトを送り、JSON形式でレスポンスを得る　4/10 えりな
    llm_response = llm(prompt.format(knowledge=knowledge), max_tokens=1024) 
    response = ResponseModel(message=llm_response)
    return response

##下記マージする方法
class CombinedResponseModel(BaseModel):
    places_message: str
    recommendations_message: str

@app.get("/combined/", response_model=CombinedResponseModel)
async def get_combined(location: str = "35.7356,139.6522"):
    # /places/ からのデータを非同期に取得
    places_response = await get_places(location=location)
    
    # /recommendations/ からのデータを非同期に取得
    # 非同期でデータを取得するためには、get_hotpepper_data 関数も非同期に対応させる必要があります。
    recommendations_response = await get_recommendations()

    # 取得したデータをマージ
    combined_response = CombinedResponseModel(
        places_message=places_response.message,
        recommendations_message=recommendations_response.message
    )

    return combined_response

  





# -----以下後ほどGoogle Map実装時に使用予定なのでこのまま残します(のりぴ)-----

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