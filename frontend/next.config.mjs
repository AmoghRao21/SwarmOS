/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Turning off strict mode helps with React Flow double-render in dev
  output: "standalone",
};

export default nextConfig;