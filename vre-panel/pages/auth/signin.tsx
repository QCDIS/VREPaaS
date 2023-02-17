import { getProviders, getSession, signIn } from "next-auth/react"
import getConfig from 'next/config'

const { publicRuntimeConfig } = getConfig()

export default function SignIn({ providers }: { providers: any }) {
    return (
        <div className="mx-auto bg-gradient-to-b from-sky-100 to-orange-300 flex flex-col items-center justify-center h-screen">
            <img className="w-fit h-fit object-cover" src={`${publicRuntimeConfig.staticFolder}/envri_summer_school.png`} />
            <div className="flex flex-col justify-center rounded-md overflow-hidden shadow-lg bg-white p-10 mt-10 w-screen">
                <img src={`${publicRuntimeConfig.staticFolder}/envri_logo_final.png`} className="w-36 self-center" alt="LifeWatch Logo" />
                <>
                    {Object.values(providers).map((provider: any) => (
                        <div className="self-center" key={provider.name}>
                            <button className="bg-blue-400/50 hover:bg-blue-400 text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow mt-10" onClick={() => signIn(provider.id, { callbackUrl: process.env.CALL_BACK_URL })}>
                                Sign in with ENVRI
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
    const providers = await getProviders()
    const session = await getSession({ req })

    if (session) {
        return {
            redirect: { destination: `${publicRuntimeConfig.basePath}/` },
        };
    }

    return {
        props: { providers },
    }
}