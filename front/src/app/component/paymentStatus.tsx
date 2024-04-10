import React, { useState, useEffect } from 'react';
import { useStripe } from '@stripe/react-stripe-js';
import { PaymentIntentResult } from '@stripe/stripe-js';

const PaymentStatus: React.FC = () => {
  const stripe = useStripe();
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!stripe) {
      return;
    }

    // URLから"payment_intent_client_secret"クエリパラメータを取得
    const clientSecret = new URLSearchParams(window.location.search).get('payment_intent_client_secret');

    if (!clientSecret) {
      setMessage('支払い意図のクライアントシークレットが見つかりません');
      return;
    }

    // PaymentIntentを取得
    stripe.retrievePaymentIntent(clientSecret).then((result: PaymentIntentResult) => {
      if (result.error) {
        setMessage(`error: ${result.error.message}`);
        return;
      }

      const paymentIntent = result.paymentIntent;

      // PaymentIntentのステータスに基づいてユーザーに表示するメッセージを設定
      switch (paymentIntent?.status) {
        case 'succeeded':
          setMessage('支払いが受けつけました');
          break;

        case 'processing':
          setMessage('支払い処理中です。支払いが受け取られ次第、お知らせします。');
          break;

        case 'requires_payment_method':
          setMessage('支払いに失敗しました。別の支払い方法をお試しください。');
          break;

        default:
          setMessage('問題が発生しました。');
          break;
      }
    });
  }, [stripe]);

  return (
    <div>
      {message ? <p>{message}</p> : <p>Loading...</p>};
    </div> 
  );
};

export default PaymentStatus;
