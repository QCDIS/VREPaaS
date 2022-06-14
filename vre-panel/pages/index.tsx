import { Hero } from "../templates/Hero";
import { Nav } from '../templates/Nav';
import useAuth from "./auth/useAuth";

const Index = () => {
    
    return (
        <div>
            <Nav />
            <Hero />
        </div>
    )
}

export default Index;