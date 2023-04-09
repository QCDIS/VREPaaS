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
    myVar: 'myVar',
    someValue: process.env.NEXT_PUBLIC_ENV_VRE_API_URL,
  }
}
