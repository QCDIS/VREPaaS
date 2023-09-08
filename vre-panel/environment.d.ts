declare namespace NodeJS {
    interface ProcessEnv {
        NEXT_PUBLIC_SECRET: string,
        KEYCLOAK_CLIENT_ID: string,
        KEYCLOAK_CLIENT_SECRET: string,
        KEYCLOAK_ISSUER: string,
        AUTH0_ID: string,
        VRE_API_TOKEN: string,
        AUTH0_SECRET: string,
        AUTH0_ISSUER: string,
        API_BASE_PATH: string,
        FRONTEND_BASE_PATH: string,
    }
}