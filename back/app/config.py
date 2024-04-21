import os
from dotenv import load_dotenv

# 環境変数をロードする
load_dotenv()


class Settings:
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    
settings = Settings()