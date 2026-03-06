/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
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
      {
        source: "/join.md",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/join.md`,
      },
    ];
  },
};

module.exports = nextConfig;
