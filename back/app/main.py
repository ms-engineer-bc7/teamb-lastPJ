from fastapi import FastAPI, HTTPException, APIRouter
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
from .stationFinder import find_station,GeocodeResponse, StationResponse, find_station_async, StationRequest
import random #4/12追加のりぴ #4/11ゆか

# 環境変数の読み込み
load_dotenv()

# 必要な環境変数を .env ファイルから読み込む
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", OPENAI_API_KEY)
stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = stripe_secret_key

# OpenAIのインスタンスを作成　生成されるテキストの予測可能性
llm = OpenAI(temperature=0.9, api_key=os.getenv("OPENAI_API_KEY"))

# 本当はベクターDBとか PDF などから動的に取得するべき。
knowledge = """
 
"""

app = FastAPI()
router = APIRouter()

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
      visit_type: str  # 訪問タイプを必須フィールドにする

class ResponseModel(BaseModel):
    message: str

# ユーザーがフロント入力した情報を元にAPIが周辺情報を取得しLLMに投げその結果を返す
@app.post("/places/")
async def get_places(query: PlaceQuery):
  try:
      # queryの内容ログに出力
    print(f"Received query: {query.dict()}")

    # 年齢が提供されていない場合は「年齢未提供」と表現し、提供されている場合は年齢を表示
    age_description = f"{query.age}歳" if query.age is not None else "年齢未提供"
    visit_type_description = f"訪問タイプ: {query.visit_type}"

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

        # {knowledge} でリスト化
        prompt = PromptTemplate(
        input_variables=["knowledge"],
        template=f"""
                {query.station}駅近くで{visit_type_description}として土日に出かけたいと考えています。
                休日の適切な過ごし方を３～４つ提案してください。過ごし方はのんびりとした時間を過ごしたいです。
                {query.station}から徒歩圏内の周辺情報も以下の場所から選んだ上でその具体的な名称も文章の初めに提示し優しい口調で教えてください：{knowledge}
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
        raise HTTPException(status_code=400, detail="このサービスは練馬駅限定です")

#-----最寄り駅からランダムに周辺の駅を取得-----#
@app.get("/find-station/")
def get_station_by_address(address: str):
    return find_station(address)

class StationRequest(BaseModel):
    station_name: str

app.include_router(router)


@app.post("/stations/", response_model=StationResponse)
async def get_station_by_address(request: StationRequest):
    try:
        # 駅の位置情報を取得する非同期関数を呼び出す
        geocode_response = await find_station_async(request.station_name + "駅")
        
         # ランダムに駅を選択する
        if geocode_response.nearby_stations:
            random_station = random.choice(geocode_response.nearby_stations)
         # 選択された駅の名前をレスポンスに設定
            return StationResponse(random_station=random_station, nearby_info=[])
        else:
            return StationResponse(random_station="Nearest station not found", nearby_info=[])

    except HTTPException as exc:
        raise exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
