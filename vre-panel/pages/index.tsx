import { useSession } from "next-auth/react";
import { useRouter } from "next/router";
import { Hero } from "../templates/Hero";
import { Nav } from '../templates/Nav';

const Index = () => {

    const { status } = useSession();
    const router = useRouter();

    if (status == "authenticated")
        router.push("/home");
    
    return (
        <div>
            <Nav />
            <Hero />
        </div>
    )
}

export default Index;