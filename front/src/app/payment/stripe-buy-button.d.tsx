// stripe-buy-button.d.ts
export {};
declare global {
    namespace JSX {
       interface IntrinsicElements {
         'stripe-buy-button': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
       }
    }
   }