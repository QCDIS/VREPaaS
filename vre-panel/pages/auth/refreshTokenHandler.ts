import { useSession } from "next-auth/react";
import { useEffect } from "react";

const RefreshTokenHandler = (props) => {
    const { data: session } = useSession();

    useEffect(() => {
        if (!!session) {
            const unixTimeZero = Date.parse('01 Jan 1970 00:00:00 GMT');
            const expiryDate = new Date();
            expiryDate.setTime(unixTimeZero)
            expiryDate.setSeconds(expiryDate.getSeconds() + session.accessTokenExpiry);
            const timeRemaining = Math.round((expiryDate.getTime() - Date.now()) / 1000);
            props.setInterval(timeRemaining > 0 ? timeRemaining : 0);
        }
    }, [session]);

    return null;
}

export default RefreshTokenHandler;