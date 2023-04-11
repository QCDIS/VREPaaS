declare namespace NodeJS {
    interface ProcessEnv {
        NEXT_PUBLIC_SECRET: string,
        KEYCLOAK_CLIENT_ID: string,
        KEYCLOAK_CLIENT_SECRET: string,
        KEYCLOAK_ISSUER: string,
        VRE_API_URL: string,
        AUTH0_ID: string,
        AUTH0_SECRET: string,
        AUTH0_ISSUER: string,
        NEXT_PUBLIC_ENV_VRE_API_URL: string
    }
}