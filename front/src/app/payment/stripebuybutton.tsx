import React, { useEffect, useState } from 'react';
import Image from 'next/image'; // Import the Image component

const StripeBuyButton: React.FC = () => {
 const [scriptLoaded, setScriptLoaded] = useState<boolean>(false);

 useEffect(() => {
    if (typeof window !== 'undefined') {
      const script = document.createElement('script');
      script.src = 'https://js.stripe.com/v3/buy-button.js';
      script.async = true;
      script.onload = () => setScriptLoaded(true);
      document.body.appendChild(script);

      return () => {
        document.body.removeChild(script);
      };
    }
 }, []);

 if (!scriptLoaded) {
    return <div>Loading...</div>;
 }

 return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <stripe-buy-button
        buy-button-id="buy_btn_1P3ZW1CpbVKijddQrZc406o7"
        publishable-key="pk_test_51P2Y0QCpbVKijddQnD0OHvWudxFghlcMlL0FMiDitKJMA0mRgyew2kzM9Bb6iRnjrYw52BJcdgxCANBrWUwGOKPs004wtvPlM6"
      >
      </stripe-buy-button>
      <Image
        src="/qr_test_28o7su5tY9Cy1he3cd copy.png"
        alt="QR Code"
        width={200} // Adjust width as needed
        height={200} // Adjust height as needed
        style={{ marginLeft: '20px' }}
      />
    </div>
 );
};

export default StripeBuyButton;


// import React, { useEffect, useState } from 'react';

// const StripeBuyButton: React.FC = () => {
//   const [scriptLoaded, setScriptLoaded] = useState(false); //4/10追加
//   useEffect(() => {
//     // クライアントサイドでのみスクリプトを追加
//     if (typeof window !== 'undefined') {
//       const script = document.createElement('script');
//       script.src = 'https://js.stripe.com/v3/buy-button.js';
//       script.async = true;
//       script.onload = () => setScriptLoaded(true);//4/10追加
//       document.body.appendChild(script);

//       return () => {
//         document.body.removeChild(script);
//       };
//     }
//   }, []);
//   if (!scriptLoaded) {
//     return <div>Loading...</div>; // Or any loading indicator
//  }
//   return (
//     <stripe-buy-button
//       buy-button-id="buy_btn_1P3ZW1CpbVKijddQrZc406o7"
//       publishable-key="pk_test_51P2Y0QCpbVKijddQnD0OHvWudxFghlcMlL0FMiDitKJMA0mRgyew2kzM9Bb6iRnjrYw52BJcdgxCANBrWUwGOKPs004wtvPlM6"
//       >
//     </stripe-buy-button>
//   );
// };

// export default StripeBuyButton;

