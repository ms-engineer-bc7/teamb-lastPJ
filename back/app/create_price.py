import stripe
stripe.api_key = "sk_test_51P2Y0QCpbVKijddQKWXbrVfloLbGn905lU9DR8RyCxZmEko2BSDim8C3vdahhMfXr1d0mvWx4TW673NK3bGnCt1K00Zmx1Iclz"
starter_subscription = stripe.Product.create(
  name="街ブラアプリ",
  description="街ブラアプリです（テスト用）",
)

starter_subscription_price = stripe.Price.create(
  unit_amount=330,
  currency="jpy",
  recurring={"interval": "month"},
  product=starter_subscription['id'],
)

# Save these identifiers
print(f"Success! Here is your starter subscription product id: {starter_subscription.id}")
print(f"Success! Here is your starter subscription price id: {starter_subscription_price.id}")
