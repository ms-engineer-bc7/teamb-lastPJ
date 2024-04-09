# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
import os

stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = stripe_secret_key
# stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
print("Stripe API Key:", stripe.api_key) # デバッグ用の行

stripe.PaymentIntent.create(
  amount=330,
  currency="jpy",
  automatic_payment_methods={"enabled": True},
)

