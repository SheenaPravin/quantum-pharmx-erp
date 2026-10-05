/** @type {import('next').NextConfig} */
const isGhPages = process.env.GITHUB_PAGES === "true";
const repoBase = "/quantum-pharmx-erp";
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  ...(isGhPages ? { basePath: repoBase, assetPrefix: `${repoBase}/` } : {}),
};
module.exports = nextConfig;
