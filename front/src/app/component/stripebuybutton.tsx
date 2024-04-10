import React, { useEffect, useState } from 'react';

const StripeBuyButton: React.FC = () => {
  const [scriptLoaded, setScriptLoaded] = useState(false); //4/10追加
  useEffect(() => {
    // クライアントサイドでのみスクリプトを追加
    if (typeof window !== 'undefined') {
      const script = document.createElement('script');
      script.src = 'https://js.stripe.com/v3/buy-button.js';
      script.async = true;
      script.onload = () => setScriptLoaded(true);//4/10追加
      document.body.appendChild(script);

      return () => {
        document.body.removeChild(script);
      };
    }
  }, []);
  if (!scriptLoaded) {
    return <div>Loading...</div>; // Or any loading indicator
 }
  return (
    <stripe-buy-button
      buy-button-id="buy_btn_1P3oEUCpbVKijddQ8Uu7qbPw"
      publishable-key="pk_test_51P2Y0QCpbVKijddQnD0OHvWudxFghlcMlL0FMiDitKJMA0mRgyew2kzM9Bb6iRnjrYw52BJcdgxCANBrWUwGOKPs004wtvPlM6"
    ></stripe-buy-button>
  );
};

export default StripeBuyButton;

// Stripeの公式のコード
{/* <script async
  src="https://js.stripe.com/v3/buy-button.js">
</script>

<stripe-buy-button
  buy-button-id="buy_btn_1P3oEUCpbVKijddQ8Uu7qbPw"
  publishable-key="pk_test_51P2Y0QCpbVKijddQnD0OHvWudxFghlcMlL0FMiDitKJMA0mRgyew2kzM9Bb6iRnjrYw52BJcdgxCANBrWUwGOKPs004wtvPlM6"
>
</stripe-buy-button> */}