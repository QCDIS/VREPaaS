declare namespace NodeJS {
    interface ProcessEnv {
        NEXTAUTH_URL: string,
        NEXT_PUBLIC_SECRET: string,
        KEYCLOAK_CLIENT_ID: string,
        KEYCLOAK_CLIENT_SECRET: string,
        KEYCLOAK_ISSUER: string,
        VRE_API_URL: string,
        AUTH0_ID: string,
        AUTH0_SECRET: string,
        AUTH0_ISSUER: string
    }
}