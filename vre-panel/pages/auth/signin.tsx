import { getProviders, getSession, signIn } from "next-auth/react"
import getConfig from 'next/config'
import {useContext} from "react";
import {PaasConfigContext} from "../../context/PaasConfig";

const { publicRuntimeConfig } = getConfig()

export default function SignIn({ providers }: { providers: any }) {

    const {paasConfig, paasConfigLoading} = useContext(PaasConfigContext)

    return (
        <div className="mx-auto flex flex-col items-center justify-center h-screen">
            <img className="w-fit h-fit object-cover" src={`${publicRuntimeConfig.staticFolder}/LW_VLICVRE_logo.png`} />
            <div className="flex flex-col justify-center rounded-md overflow-hidden shadow-lg bg-white p-10 mt-10 w-screen">
                {paasConfigLoading || (
                    <img
                        src={paasConfig.site_icon}
                        alt="Site icon"
                        className="h-16 self-center"
                    />
                )}
                <>
                    {Object.values(providers).map((provider: any) => (
                        <div className="self-center" key={provider.name}>
                            <button className="bg-blue-400/50 hover:bg-blue-400 text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow mt-10" onClick={() => signIn(provider.id, { callbackUrl: process.env.CALL_BACK_URL })}>
                                Sign in with {provider.name}
                            </button>
                        </div>
                    ))}
                </>
            </div>
        </div>
    )
}

export async function getServerSideProps(context: { req: any, query: any}) {

    const { req, query } = context;
    console.log("getProviders")
    const redirectUrl = query.callbackUrl ? query.callbackUrl : '/'
    const providers = await getProviders()
    const session = await getSession({ req })
    if (session) {
        console.log("Session exists, redirecting to", redirectUrl)
        return {
            redirect: { destination: redirectUrl },
        };
    }
    console.log("providers: ", providers)
    return {
        props: { providers },
    }
}