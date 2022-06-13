declare namespace NodeJS {
    interface ProcessEnv {
        NEXTAUTH_URL: string
        NEXT_PUBLIC_SECRET: string
        KEYCLOAK_CLIENT_ID: string
        KEYCLOAK_CLIENT_SECRET: string
        KEYCLOAK_ISSUER: string
    }
}