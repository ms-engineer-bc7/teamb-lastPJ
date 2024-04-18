from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, select, update, Column, String, Integer
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# データベース接続とセッションの設定
DATABASE_URL = "postgresql://teamb:password@db/teamb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# すでにデータベースに存在するモデル/テーブルを使用する場合、
# ここにクラス定義を同期させる
class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    user_type = Column(String)
    api_calls = Column(Integer, default=0)

# 依存関係定義: 各リクエストでデータベースセッションを生成し、完了後に閉じる
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserRequest(BaseModel):
    username: str
    request_text: str

@app.get("/request-recommendation/")
async def request_recommendation(user_request: UserRequest, db: Session = Depends(get_db)):
    logger.info(f"Request for username: {user_request.username}")  # ユーザ名でのリクエストを記録
    user = db.query(User).filter(User.username == user_request.username).first()
    if not user:
        logger.error("User not found")  # ユーザが見つからない場合のエラーログ
        raise HTTPException(status_code=404, detail="User not found")

    text_length = len(user_request.request_text)
    allowed_length = 100 if user.user_type == "free" or (user.user_type == "member" and user.api_calls >= 3) else None
    if allowed_length is not None and text_length > allowed_length:
        logger.warning(f"Text limit exceeded for user {user_request.username}")  # テキスト制限超過の警告ログ
        raise HTTPException(status_code=400, detail=f"Text limit exceeded. Max allowed: {allowed_length} characters")

    if user.user_type == "member":
        user.api_calls += 1
        db.commit()
        logger.info(f"API call count updated to {user.api_calls} for user {user_request.username}")  # APIコール数の更新を記録


    recommendation = f"あなたの入力に基づく提案: {user_request.request_text[:allowed_length if allowed_length is not None else len(user_request.request_text)]}"
    logger.info(f"Recommendation provided for {user_request.username}")  # おすすめプランが提供されたことを記録
    return {"おすすめプランの提案": recommendation}

# ここで`create_all`を呼び出す必要はありません。



