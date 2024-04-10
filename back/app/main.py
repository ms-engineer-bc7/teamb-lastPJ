from fastapi import FastAPI
import os
import stripe #stripeをインポート
from dotenv import load_dotenv
import requests
from langchain_openai import OpenAI # OpenAIをインポート
from langchain.prompts import PromptTemplate
from pydantic import BaseModel #PydanticのBaseModel追加　4/9のりぴ
from .routes.hotpepper import get_hotpepper_data #horpepperのデータを追加　4/9えりな



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

class ResponseModel(BaseModel):#追加　4/9のりぴ
    message: str

# エンドポイント/placesとどちらでもいいが統一する
@app.get("/places/")
async def get_places(location: str = "35.7356,139.6522", query: str = "公園", radius: int = 2000, language: str = "ja"):
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

    # OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
    #文字数を増やすと下記コードになる
    res = llm(prompt.format(knowledge=knowledge), max_tokens=1024) 
    return res
  





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