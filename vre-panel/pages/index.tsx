import { getToken } from 'next-auth/jwt';
import { signIn, useSession } from 'next-auth/react';
import getConfig from 'next/config';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { NewVREDialog } from '../components/NewVREDialog';
import { Nav } from '../templates/Nav';
// import useAuth from './auth/useAuth';

const { publicRuntimeConfig } = getConfig()

const getSlug = (title: string) => {

    return title
        .toLowerCase()
        .replace(/ /g, '-')
        .replace(/[^\w-]+/g, '');
}

const VLabs = () => {

    // const isAuthenticated = useAuth(true);
    const [isOpen, setIsOpen] = useState(false);
    const [vlabs, setVlabs] = useState([]);

    useEffect(() => {

        // if (isAuthenticated) {

            // var requestOptions: RequestInit = {
            //     method: "GET",
            //     headers: {
            //         "Authorization": "Bearer: " + token.accessToken
            //     },
            // };
            const vre_api_url = process.env.NEXT_PUBLIC_ENV_VRE_API_URL
            
            fetch(`${vre_api_url}/vlabs`)
                .then((res) => res.json())
                .then((data) => {
                    setVlabs(data);
                })
                .catch((error) => {
                    console.log(error)
                });
        // }
    }, []);

    // const { status } = useSession({
    //     required: true,
    //     onUnauthenticated() {
    //         signIn();
    //     },
    // })

    // if (status === "loading") {
    //     return "Loading or not authenticated..."
    // }

    return (
        <div>
            <Nav />
            <div className='min-h-screen mx-auto bg-gradient-to-b from-sky-100 to-orange-300'>
                <div className='grid grid-cols-3'>
                    {vlabs.map((vlab: any) => {
                        return (
                            <div key={getSlug(vlab.title)} className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-10">
                                <Link
                                    href={{
                                        pathname: '/vlabs/[slug]',
                                        query: { slug: vlab.slug }
                                    }}
                                    as={`${publicRuntimeConfig.basePath}/vlabs/${vlab.slug}`}
                                >
                                    <div>
                                        <img className="w-35 h-30 object-cover" src={`${publicRuntimeConfig.staticFolder}/HP-VRES.png`} />
                                        <div className="font-bold text-l mb-2 bg-blue-500 text-white p-5">{vlab.title}</div>
                                        <div className="px-3 py-2">
                                            <p className="text-gray-700 text-base truncate ...">
                                                {vlab.description}
                                            </p>
                                        </div>
                                    </div>
                                </Link>
                            </div>
                        );
                    })}
                </div>
                <NewVREDialog isOpen={isOpen} setIsOpen={setIsOpen} />
            </div>
        </div >
    )
};

export async function getServerSideProps(context) {

    const { req } = context;
    const secret = process.env.SECRET;
    const token = await getToken({ req, secret });

    return {
        props: {
            token: token
        }
    };
}

export default VLabs;