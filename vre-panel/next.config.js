console.log(process.env.NODE_ENV);

module.exports = {
  reactStrictMode: true,
  experimental: {
    outputStandalone: true
  },
  assetPrefix: process.env.NODE_ENV === "production" ? '/vreapp' : '',
  publicRuntimeConfig: {
    basePath: process.env.NODE_ENV === "production" ? '/vreapp' : '',
    staticFolder: process.env.NODE_ENV === "production" ? '/vreapp' : '',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_ENV_VRE_API_URL,
  }
}
