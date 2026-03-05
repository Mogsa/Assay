/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/health`,
      },
      {
        source: "/skill.md",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/skill.md`,
      },
    ];
  },
};

module.exports = nextConfig;
