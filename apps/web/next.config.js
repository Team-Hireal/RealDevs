/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // No need for output config on Vercel with @vercel/next
  // API rewrites only for local development
  async rewrites() {
    // In production (Vercel), API routes are handled by Flask via vercel.json routes
    // In development, proxy to local Flask server
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ]
    }
    return []
  },
}

module.exports = nextConfig

