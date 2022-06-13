import { signIn, useSession } from 'next-auth/react';
import { Nav } from '../templates/Nav';

const Home = () => {

    const { status } = useSession({
        required: true,
        onUnauthenticated() {
            signIn();
        },
    })

    if (status === "loading") {
        return "Loading or not authenticated..."
    }

    return (
        <div>
            <Nav />
            <div className='min-h-screen mx-auto bg-gradient-to-b from-sky-100 to-orange-300'>
                <div className='flex flex-row'>

                </div>
            </div>
        </div>
    )
}

export default Home;