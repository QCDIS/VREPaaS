

module.exports = {
  env: {
    vre_api_url: 'http://localhost:8000/api',
  },

  reactStrictMode: true,
  experimental: {
    outputStandalone: true
  },
  assetPrefix: process.env.NODE_ENV === "production" ? '/vreapp' : '',
  publicRuntimeConfig: {
    basePath: process.env.NODE_ENV === "production" ? '/vreapp' : '',
    staticFolder: process.env.NODE_ENV === "production" ? '/vreapp' : '',
  }
}
