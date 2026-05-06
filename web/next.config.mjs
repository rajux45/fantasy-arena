/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@fantasy-arena/shared'],
  experimental: {
    typedRoutes: false,
  },
};

export default nextConfig;
