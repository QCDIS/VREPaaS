console.log(process.env.NODE_ENV);

module.exports = {
  reactStrictMode: true,
  experimental: {
    outputStandalone: true
  },
  basePath: process.env.NEXT_PUBLIC_ENV_BASE_PATH,
  publicRuntimeConfig: {
    basePath: process.env.NEXT_PUBLIC_ENV_BASE_PATH,
    staticFolder: process.env.NEXT_PUBLIC_ENV_BASE_PATH,
    NEXT_PUBLIC_ENV_VRE_API_URL: process.env.NEXT_PUBLIC_ENV_VRE_API_URL
  }
}
