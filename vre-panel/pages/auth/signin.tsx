import { getProviders, getSession, signIn } from "next-auth/react"
import getConfig from 'next/config'

const { publicRuntimeConfig } = getConfig()

export default function SignIn({ providers }: { providers: any }) {
    return (
        <div className="mx-auto flex flex-col items-center justify-center h-screen">
            <img className="w-10 self-center" src={`${publicRuntimeConfig.staticFolder}/minisite-banner-2048x773.png`} />
            <img className="w-fit h-fit object-cover" src={`${publicRuntimeConfig.staticFolder}/LW_VLICVRE_logo.png`} />
            <div className="flex flex-col justify-center rounded-md overflow-hidden shadow-lg bg-white p-10 mt-10 w-screen">
                <img src={`${publicRuntimeConfig.staticFolder}/LW_ERIC_Logo.png`} className="w-36 self-center" alt="LifeWatch Logo" />
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

export async function getServerSideProps(context: { req: any; }) {

    const { req } = context;
    console.log("getProviders")
    const providers = await getProviders()
    const session = await getSession({ req })
    if (session) {
        console.log("Session exists, redirecting to", '/')
        return {
            redirect: { destination: '/' },
        };
    }
    console.log("providers: ", providers)
    return {
        props: { providers },
    }
}