/** @type {import('next').NextConfig} */
const nextConfig = {

    reactStrictMode: true,
    swcMinify: true,
};
    env: {
       STRIPE_PUBLIC_KEY: process.env.STRIPE_PUBLIC_KEY,
    },
   };

export default nextConfig;
