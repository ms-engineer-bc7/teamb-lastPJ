// utils/stripe.ts
// import axios from 'axios';

// export const getStripeCustomerId = async (uid: string): Promise<string | null> => {
//   try {
//     const response = await axios.get(`http://localhost:8000/users/${uid}/stripe-customer-id`);
//     return response.data.stripeCustomerId || null;
//   } catch (error) {
//     console.error('Error fetching Stripe customer ID:', error);
//     return null;
//   }
// };