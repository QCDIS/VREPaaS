import { getToken } from 'next-auth/jwt';
import { signIn, useSession } from 'next-auth/react';
import getConfig from 'next/config';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { NewVREDialog } from '../components/NewVREDialog';
import { Nav } from '../templates/Nav';
import useAuth from './auth/useAuth';

const { publicRuntimeConfig } = getConfig()

const getSlug = (title: string) => {

    return title
        .toLowerCase()
        .replace(/ /g, '-')
        .replace(/[^\w-]+/g, '');
}

const VLabs = () => {

    //const isAuthenticated = useAuth(true);
    const [isOpen, setIsOpen] = useState(false);
    const [vlabs, setVlabs] = useState([]);
    const session = useSession();
    const StudentPlaceholder = {
        keycloak_ID: "Loading ..",
        name: "",
        assignments_enrolled: "",
    }
    const [Stud, setStud] = useState(StudentPlaceholder)
    var userProcessed = false;
    var userName = '';

       
   
    useEffect(() => {
        // if (isAuthenticated) {

            // var requestOptions: RequestInit = {
            //     method: "GET",
            //     headers: {
            //         "Authorization": "Bearer: " + token.accessToken
            //     },
            // };
            if (session && !userProcessed) {
                try{
                    console.log(session.data.user.name);
                    userName = session.data.user.name;
                    if (!userProcessed){
                        const url2 = new URL("http://localhost:8000/api/students/");
                        const url = 'http://localhost:8000/api/students/'
                        const data = {
                            keycloak_ID: userName,
                            slug: userName,
                        };
                        console.log(JSON.stringify(data));
                        fetch(`${url}`, {
                            method: "POST",
                            headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(data)
                        })
                        .then((response) => response.json())
                        .then((data) => {
                            console.log(data);
                            userProcessed = true;
                            console.log('user processed')
                        });
                    }
                }
                catch 
                {
    
                    console.log('err')
                };
            }
         
            const vre_api_url = process.env.NEXT_PUBLIC_ENV_VRE_API_URL
            
            const url = new URL("http://localhost:8000/api/vlabs");
            const url2 = new URL("http://localhost:8000/api/assignments");
            console.log(url);
            
            fetch(url2)
                .then((res) => res.json())
                .then((data) => {
                    setVlabs(data);
                })
                .catch((error) => {
                    console.log('Featching error:'+error)
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
                                        pathname: '/assignments/[slug]',
                                        query: { slug: vlab.slug }
                                    }}
                                    as={`${publicRuntimeConfig.basePath}/assignments/${vlab.slug}`}
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
                {/* <div key="Kev" className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-10">
                                <Link
                                    href={{
                                        pathname: '/new_assignment',
                                    }}
                                    as={`${publicRuntimeConfig.basePath}/new_assignment`}
                                   >
                                    <div>
                                        <div className="px-3 py-2">
                                        <p>Create new assignments</p>
                                        </div>
                                    </div>
                                </Link>
                            
                        
                </div> */}
                <NewVREDialog isOpen={isOpen} setIsOpen={setIsOpen} />
            </div>
        </div >
    )
    // return (
    //     <div>
    //         <Nav />
    //         <div className='min-h-screen mx-auto bg-gradient-to-b from-sky-100 to-orange-300'>
    //             <div className='grid grid-cols-3'>
    //                 {vlabs.map((vlab: any) => {
    //                     return (
    //                         <div key={getSlug(vlab.title)} className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-10">
    //                             <Link
    //                                 href={{
    //                                     pathname: '/vlabs/[slug]',
    //                                     query: { slug: vlab.slug }
    //                                 }}
    //                                 as={`${publicRuntimeConfig.basePath}/vlabs/${vlab.slug}`}
    //                             >
    //                                 <div>
    //                                     <img className="w-35 h-30 object-cover" src={`${publicRuntimeConfig.staticFolder}/HP-VRES.png`} />
    //                                     <div className="font-bold text-l mb-2 bg-blue-500 text-white p-5">{vlab.title}</div>
    //                                     <div className="px-3 py-2">
    //                                         <p className="text-gray-700 text-base truncate ...">
    //                                             {vlab.description}
    //                                         </p>
    //                                     </div>
    //                                 </div>
    //                             </Link>
    //                         </div>
    //                     );
    //                 })}
    //             </div>
    //             <NewVREDialog isOpen={isOpen} setIsOpen={setIsOpen} />
    //         </div>
    //     </div >
    // )
};

export async function getServerSideProps(context:any) {

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