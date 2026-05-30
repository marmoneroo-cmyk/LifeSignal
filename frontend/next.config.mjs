/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // In production on Vercel, /api/* routes to the Python serverless function via
  // vercel.json rewrites. In local dev, proxy /api/* to the uvicorn backend
  // (NEXT_PUBLIC_API_URL or default localhost:8000) so the frontend can keep
  // using same-origin relative paths everywhere.
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    const target = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [
      { source: "/api/:path*", destination: `${target}/api/:path*` },
    ];
  },
};

export default nextConfig;
