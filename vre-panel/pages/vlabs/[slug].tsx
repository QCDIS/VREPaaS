import { getToken } from "next-auth/jwt";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { Nav } from "../../templates/Nav";
import useAuth from "../auth/useAuth";


const VLabDetails = ({ token }) => {

    const vlabPlaceholder = {
        title: "Loading ..",
        slug: "",
        description: "Loading ..",
        endpoint: ""
    }
    const isAuthenticated = useAuth(true);
    const router = useRouter();
    const { slug } = router.query;
    const [vlab, setVlab] = useState(vlabPlaceholder)
    const [workflows, setWorkflows] = useState([])
    const [loadingWorkflow, setLoadingWorkflows] = useState(false)

    const fetchVlab = async () => {

        var requestOptions: RequestInit = {
            method: "GET",
            headers: {
                "Authorization": "Bearer: " + token.accessToken
            },
        };

        const url = process.env.NEXT_PUBLIC_ENV_VRE_API_URL;

        const res = await fetch(`${url}/vlabs/${slug}`, requestOptions);
        return res.json();
    }

    const fetchWorkflows = async () => {

        setLoadingWorkflows(true);

        var requestOptions: RequestInit = {
            method: "GET",
            headers: {
                "Authorization": "Bearer: " + token.accessToken
            },
        };

        const url = process.env.NEXT_PUBLIC_ENV_VRE_API_URL;
        const res = await fetch(`${url}/workflows?vlab_slug=${slug}`, requestOptions);
        console.log('res vlabs: '+res.json())
        setLoadingWorkflows(false);

        return res.json();
    }

    useEffect(() => {
        if (isAuthenticated) {
            Promise.all([
                fetchVlab().then(setVlab),
                fetchWorkflows().then(setWorkflows)
            ])
        }
    }, [isAuthenticated]);


    const getSpinningButtonClass = () => {
        if (loadingWorkflow) {
            return "w-5 h-5 animate-spin";
        }
        return "w-5 h-5";
    }

    return (
        <div>
            <Nav />
            <div className="grid grid-flow-row-dense grid-cols-4 grid-rows-3 gap-4 p-5 min-h-screen mx-auto bg-gradient-to-b from-sky-100 to-orange-300">
                <div className="row-span-4 col-span-2 shadow-lg bg-white p-10">
                    <p className="text-4xl font-sans">{vlab.title}</p>
                    <a target="blank" href={vlab.endpoint}>
                        <button className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded mt-5">
                            Launch
                        </button>
                    </a>
                    <p className="h-64 mt-5 text-justify">{vlab.description}</p>
                </div>
                <div className="row-span-2 col-span-2 shadow-lg bg-white p-10">
                    <p className="text-2xl font-sans">Workflows Runs</p>
                    <button type="button"
                        className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded mt-5 cursor-pointer"
                        onClick={() => {fetchWorkflows().then(setWorkflows)}}>
                        <svg xmlns="http://www.w3.org/2000/svg" className={getSpinningButtonClass()} viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd"
                                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                                clipRule="evenodd" />
                        </svg>
                    </button>
                    <table className="table-auto bg-white mt-5">
                        <thead>
                            <tr>
                                <th className="bg-blue-200 border text-left px-8 py-4">Name</th>
                                <th className="bg-blue-200 border text-left px-8 py-4">Status</th>
                                <th className="bg-blue-200 border text-left px-8 py-4">Progress</th>
                            </tr>
                        </thead>
                        {vlab != null ? (
                            <tbody>
                                {workflows.map((workflow) => {
                                    return (
                                        <tr key={workflow['argo_id']} className="odd:bg-gray-100">
                                            <td className={"border py-2 px-4"}>
                                                <a className="underline text-blue-600 hover:text-blue-800 visited:text-purple-600"
                                                    target="blank"
                                                    href={workflow['argo_url']}>
                                                    {workflow['argo_id']}
                                                </a>
                                            </td>
                                            <td className={"border py-2 px-4 text-center"}>{workflow['status']}</td>
                                            <td className={"border py-2 px-4 text-center"}>{workflow['progress']}</td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        ) : (
                            <tbody>
                            </tbody>
                        )}
                    </table>
                </div>
                <div className="row-span-2 col-span-2 shadow-lg bg-white p-10">
                    <p className="text-2xl font-sans">Catalogs</p>
                </div>
            </div>
        </div>
    )

}

export default VLabDetails;

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