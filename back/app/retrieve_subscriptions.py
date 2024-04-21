# stripeのサブスク一覧取得
import os
import stripe
import logging

# 環境変数からStripeの秘密鍵を取得
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# ロギング設定
logging.basicConfig(level=logging.INFO, filename='subscriptions.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# サブスクリプション一覧の取得
subscriptions = stripe.Subscription.list(limit=10)

for subscription in subscriptions.auto_paging_iter():
    # コンソールとログファイルに出力
    log_msg = f"ID: {subscription.id}, Customer: {subscription.customer}, Status: {subscription.status}"
    print(log_msg)
    logging.info(log_msg)