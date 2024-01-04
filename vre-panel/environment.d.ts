declare namespace NodeJS {
    interface ProcessEnv {
        NEXT_PUBLIC_SECRET: string,
        AUTH0_ID: string,
        AUTH0_SECRET: string,
        AUTH0_ISSUER: string,
        API_BASE_PATH: string,
        FRONTEND_BASE_PATH: string,
    }
}