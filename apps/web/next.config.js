/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Only export as static site in production to avoid ISR functions counting against Vercel limit
  // In development, we need rewrites to work for API proxying
  ...(process.env.NODE_ENV === 'production' && { output: 'export' }),
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
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

