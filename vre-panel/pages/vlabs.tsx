import { Nav } from '../templates/Nav';
import { NewVREDialog } from '../components/NewVREDialog';
import { useEffect, useState } from 'react';
import { useSession, signIn } from 'next-auth/react';
import Link from 'next/link';
import { getToken } from 'next-auth/jwt';
import useAuth from './auth/useAuth';
import getConfig from 'next/config'

const { publicRuntimeConfig } = getConfig()

const getSlug = (title: string) => {

    return title
        .toLowerCase()
        .replace(/ /g, '-')
        .replace(/[^\w-]+/g, '');
}

const VLabs = ({ token }) => {

    const isAuthenticated = useAuth(true);
    const [isOpen, setIsOpen] = useState(false);
    const [vlabs, setVlabs] = useState([]);

    useEffect(() => {

        if (isAuthenticated) {

            var requestOptions: RequestInit = {
                method: "GET",
                headers: {
                    "Authorization": "Bearer: " + token.accessToken
                },
            };

            fetch('https://lfw-ds001-i022.lifewatch.dev:32443/vre-api/api/vlabs/', requestOptions)
                .then((res) => res.json())
                .then((data) => {
                    console.log(data);
                    setVlabs(data);
                })
                .catch((error) => {
                    console.log(error)
                });
        }
    }, [isAuthenticated]);

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
                    {vlabs.map((vlab: any) => {
                        return (
                            <div key={getSlug(vlab.title)} className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-10 w-3/6">
                                <img className="w-full h-40 object-cover" src={`${publicRuntimeConfig.staticFolder}/lab_icon.png`} />
                                <div className="font-bold text-l mb-2 bg-blue-300 text-white p-5">{vlab.title}</div>
                                <div className="px-6 py-4">
                                    <p className="text-gray-700 text-base truncate ...">
                                        {vlab.description}
                                    </p>
                                </div>
                                <Link href="#" passHref>
                                    <div></div>
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
    const secret = "685be204b197364afdd9111d6fb5e87b";
    const token = await getToken({ req, secret });

    return {
        props: {
            token: token
        }
    };
}

export default VLabs;