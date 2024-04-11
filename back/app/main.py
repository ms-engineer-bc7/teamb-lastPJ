from fastapi import FastAPI, HTTPException
import os
import stripe #stripeをインポート
from dotenv import load_dotenv
import requests
import httpx
from langchain_openai import OpenAI # OpenAIをインポート
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field  #PydanticのBaseModel追加　4/9のりぴ　# Fieldをインポート 
from .routes.hotpepper import get_hotpepper_data #horpepperのデータを追加　4/9えりな
from fastapi.middleware.cors import CORSMiddleware #CORS設定 4/10のりぴ
from .routes.directions import router as directions_router #4/11えりな
from .geocode import find_nearest_station, GeocodeResponse #4/11ゆか
from .stationFinder import find_station,GeocodeResponse

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



# --POST検証のため一時的に/places/のGET消しています　4/11のりぴ--
# directions ルーターを追加 4/11えりな
app.include_router(directions_router)

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

@app.get("/")
def read_root():
    return {"Hello": "BuRaRi-さんぽっと-"}

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

  
class PlaceQuery(BaseModel):
      location: str
      query: str
      radius: int
      language: str
      age: int = None  # 年齢をオプショナルにする
      station: str  
      child_age: int = Field(default=None, example=5)  # 子供の年齢フィールドを追加  # 子供の年齢フィールドを追加
    #   employment: str  # 雇用形態（例: "時短勤務", "正社員", "シフト勤務"）
    #   marital_status: str = None  # 結婚状況（例: "独身", "既婚"）
    #   lifestyle: str  # ライフスタイル（例: "電車移動", "徒歩", "自転車"）

class ResponseModel(BaseModel):
    message: str

# ユーザーがフロントで選択した場所[公園等]の情報をAPIが取得しLLMに投げその結果を返す
@app.post("/places/")
async def get_places(query: PlaceQuery):
  try:
      # queryの内容ログに出力
    print(f"Received query: {query.dict()}")

    # 年齢が提供されていない場合は「年齢未提供」と表現し、提供されている場合は年齢を表示
    age_description = f"{query.age}歳" if query.age is not None else "年齢未提供"
    child_age_description = f"子供は{query.child_age}歳" if query.child_age is not None else "子供の年齢未提供"

    # APIリクエスト
    google_places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(google_places_url, params = {
        'key': GOOGLE_MAPS_API_KEY,
        'location': query.location,
        'radius': query.radius,
        'language': query.language,
        'keyword': query.query,
    })
        # ここで応答のステータスコードと内容をログに出力する
        print(f"Google Places API response status: {resp.status_code}")
        print(f"Google Places API response data: {resp.json()}")

        if resp.status_code != 200:
            # エラークライアントに返す
            raise HTTPException(status_code=resp.status_code, detail=resp.text)

        # LLMにデータを渡し、処理を行う部分を実装。
        # ここではGoogle Places APIから得たデータをそのまま返しています。
        places_data = resp.json()

        # 取得した場所の名前のリストを作る　places_namesがリスト
        places_names = [place['name'] for place in places_data.get('results', [])]

        # レスポンスにOpenAIを利用して加工を行う　取得データをLLMに投げている部分
        # places_namesを文字列に変換しknowledge 変数に格納しプロンプトの一部としてLangChain LLMに送る
        knowledge = f"以下の場所が見つかりました：{', '.join(places_names)}"


        prompt = PromptTemplate(
        input_variables=["knowledge"],
        template=f"""
        {knowledge}

        {query.station}駅近くに住む{age_description}の女性です。
        現在の最寄り駅の近くで、土日に{child_age_description}と出かけたい。
        休日の適切な過ごし方を優しく柔らかい口調で具体的な場所の名称も用いて３～４個提案して欲しい。
        
        """,
        )

        # OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
        # 文字数増やすコード追加
        llm_response = llm(prompt.format(knowledge=knowledge), max_tokens=1500)

        # LLMのレスポンスをResponseModelの形式に合わせて整形 JSONに直す
        response = ResponseModel(message=llm_response)
        return response
    
  except Exception as e:
          raise HTTPException(status_code=500, detail=f"内部エラーが発生しました: {str(e)}")



        # プロンプトの条件分岐
    # if query.age >= 30 and query.child_age == 5:
    #     scenario = 1
    # elif query.age in range(25, 40) and query.employment == "正社員":
    #     scenario = 2
    # elif query.age >= 40 and query.marital_status == "独身":
    #     scenario = 3
    # else:
    #     scenario = None

    # if scenario == 1:
    #     prompt_text = f"""
    #     {knowledge}
    #     {query.station}駅近くに住む{query.age}代女性、{query.child_age}歳の家族がいて、
    #     現在の最寄り駅の近くで、土日にその家族と出かけたい。
    #     休日の適切な過ごし方を優しく柔らかい口調で具体的な場所の名称も用いて３～４個提案して欲しい。
    #     """
    # elif scenario == 2:
    #     prompt_text = f"""
    #     {knowledge}
    #     {query.station}駅から徒歩10分の{query.age}代の会社員が、平日は仕事が忙しく、
    #     自宅近くで休日に行ける場所の提案を親切に提案して欲しい。
    #     """
    # elif scenario == 3:
    #     prompt_text = f"""
    #     {knowledge}
    #     {query.station}駅から徒歩5分の場所に住む{query.age}代女性、独身でシフト勤務、
    #     不規則な休みを利用して、家の近くで一人で行ける場所の提案を優しく行って欲しい。
    #     """
    # else:
    #     prompt_text = "該当するシナリオがありません。詳細を確認してください。"

    # #  OpenAIにプロンプトを送り、レスポンスを得る　res=angChain LLMからの応答 指定したシナリオに基づいた内容を含む
    #     # 文字数増やすコード追加
    #     llm_response = llm(prompt.format(knowledge=knowledge), max_tokens=1500)

    #     # LLMのレスポンスをResponseModelの形式に合わせて整形 JSONに直す
    #     response = ResponseModel(message=llm_response)
    #     return response




        
    
#-----位置情報4/11（不特定多数）-----
# @app.get("/nearest-station/", response_model=GeocodeResponse)
# async def nearest_station_endpoint(address: str):
#     return find_nearest_station(address)

#-----練馬駅オンりー検索のみ-----#
@app.get("/nearest-station/", response_model=GeocodeResponse)
async def nearest_station_endpoint(address: str):
    if "練馬駅" in address:
        return find_nearest_station(address)
    else:
        raise HTTPException(status_code=400, detail="This service is for Nerima Station only.")

#-----最寄り駅からランダムに周辺の駅を取得-----#
@app.get("/find-station/")
def get_station_by_address(address: str):
    return find_station(address)

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