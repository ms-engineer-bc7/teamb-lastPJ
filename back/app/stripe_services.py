import stripe
from .config import settings

# Stripe APIキーを設定
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_customer(user_email):
    try:
        # StripeのCustomerオブジェクトを作成
        customer = stripe.Customer.create(
            email=user_email
        )
        return customer.id  # 作成された顧客のIDを返す
    except stripe.error.StripeError as e:
        # Stripe API呼び出しでエラーが発生した場合、エラーメッセージを表示
        print(f"Stripe API error occurred: {e}")
        return None
