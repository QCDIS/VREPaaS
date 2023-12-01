import { signIn, signOut, useSession } from "next-auth/react";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

export default function useAuth(shouldRedirect: boolean) {

    const { data: session } = useSession();
    const router = useRouter();
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {

        if (session?.error === "RefreshAccessTokenError") {
            signOut({ redirect: shouldRedirect });
        }

        if (session === null) {
            setIsAuthenticated(false);
            if (router.isReady && (router.route !== `/auth/signin`)) {
                const callbackUrl = `${router.basePath}${router.asPath}`
                Promise.all([
                  signIn('keycloak', {callbackUrl: callbackUrl}),
                ])
            }
        }

        else if (session !== undefined) {
            setIsAuthenticated(true);
        }

    }, [session, router.isReady]);

    return isAuthenticated;
}