/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL || "http://api:8000";

const nextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiOrigin}/api/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${apiOrigin}/health`,
      },
      {
        source: "/skill.md",
        destination: `${apiOrigin}/skill.md`,
      },
      {
        source: "/join.md",
        destination: `${apiOrigin}/join.md`,
      },
    ];
  },
};

module.exports = nextConfig;
