/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
    env: {
      STRIPE_PUBLIC_KEY: process.env.STRIPE_PUBLIC_KEY,
    },
    experimental: {
      appDir: true,
    },
    webpack: (config, { isServer, dev }) => {
      if (!isServer && dev) {
        config.watchOptions = {
          poll: 100, // 300ミリ秒ごとにポーリング(定期的にチェックする)
          aggregateTimeout: 200,
        };
      }
    // webpack(config) {
    //   config.resolve.modules.push('src', 'public');


      return config;
    },
  };
  
  export default nextConfig;
  