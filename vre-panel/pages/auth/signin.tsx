import { getProviders, getSession, signIn } from "next-auth/react"

export default function SignIn({ providers }: { providers: any }) {
    return (
        <div className="mx-auto bg-gradient-to-b from-sky-100 to-orange-300 flex items-center justify-center h-screen">
            <div className="flex flex-col justify-center rounded-md overflow-hidden shadow-lg bg-white p-10">
                <img src="/LW_ERIC_Logo.png" className="w-36 self-center" alt="LifeWatch Logo" />
                <>
                    {Object.values(providers).map((provider: any) => (
                        <div key={provider.name}>
                            <button onClick={() => signIn(provider.id)} className="bg-white hover:bg-gray-100 text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow mt-10">
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
    const providers = await getProviders()
    const session = await getSession({ req })

    if (session) {
        return {
            redirect: { destination: "/home" },
        };
    }

    return {
        props: { providers },
    }
}