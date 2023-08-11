import { signOut, useSession } from "next-auth/react";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import getConfig from "next/config";

export default function useAuth(shouldRedirect: boolean) {
    
    const { publicRuntimeConfig } = getConfig()
    const { data: session } = useSession();
    const router = useRouter();
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {

        if (session?.error === "RefreshAccessTokenError") {

            signOut({ callbackUrl: `${publicRuntimeConfig.basePath}/auth/signin`, redirect: shouldRedirect });
        }

        if (session === null) {

            if (router.route !== `${publicRuntimeConfig.basePath}/auth/signin`) {
                router.replace(`${publicRuntimeConfig.basePath}/auth/signin`);
            }

            setIsAuthenticated(false);
        } 
        
        else if (session !== undefined) {

            if (router.route === `${publicRuntimeConfig.basePath}/auth/signin`) {
                router.replace('/');
            }

            setIsAuthenticated(true);
        }

    }, [session]);

    return isAuthenticated;
}