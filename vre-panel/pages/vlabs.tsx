import { Nav } from '../templates/Nav';
import { NewVREDialog } from '../components/NewVREDialog';
import { useEffect, useState } from 'react';
import { useSession, signIn } from 'next-auth/react';
import Link from 'next/link';
import { getToken } from 'next-auth/jwt';

const VLabs = ({ token }) => {

    const [isOpen, setIsOpen] = useState(false);
    const [vlabs, setVlabs] = useState([]);

    useEffect(() => {

        var requestOptions: RequestInit = {
            method: "GET",
            headers: {
                "Authorization": "Bearer: " + token.accessToken
            },
        };

        fetch('http://localhost:8000/api/vlabs/', requestOptions)
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
                setVlabs(data);
            })
            .catch((error) => {
                console.log(error)
            });
    }, []);

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
                            <div key={vlab.name} className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-10 w-3/6">
                                <img className="w-full h-40 object-cover" src="lab_icon.png" />
                                <div className="px-6 py-4">
                                    <div className="font-bold text-l mb-2">{vlab.title}</div>
                                    <p className="text-gray-700 text-base">
                                        {vlab.description}
                                    </p>
                                </div>
                                <Link href="#" passHref>
                                    <button className="ml-5 mb-5 bg-blue-300 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded">Join</button>
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
    const token = await getToken({req, secret});

    console.log(token);

    return {
        props: {
            token: token
        }
    };
}

export default VLabs;