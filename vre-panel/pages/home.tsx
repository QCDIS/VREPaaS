import { Nav } from '../templates/Nav';
import useAuth from './auth/useAuth';

const Home = () => {

    const _isAuthenticated = useAuth(true);

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