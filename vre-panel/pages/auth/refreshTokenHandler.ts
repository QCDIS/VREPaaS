import { useSession } from "next-auth/react";
import { useEffect } from "react";

const RefreshTokenHandler = (props:any) => {
    const { data: session } = useSession();

    useEffect(() => {
        if(!!session) {
            const timeRemaining = Math.round((((session.accessTokenExpiry - 30 * 60 * 100) - Date.now()) / 1000));
            console.log(timeRemaining);
            props.setInterval(timeRemaining > 0 ? timeRemaining : 0);
        }
    }, [session]);

    return null;
}

export default RefreshTokenHandler;