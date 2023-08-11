import Link from 'next/link';
import { Menu, Transition } from '@headlessui/react';
import { useSession, signIn, signOut } from "next-auth/react"
import getConfig from 'next/config'


const Nav = () => {

    const { publicRuntimeConfig } = getConfig()
    const { data: session, status } = useSession()

    return (
        <header className="sticky top-0 z-30 w-full px-2 py-4 bg-white sm:px-4 shadow-xl">
            <nav className="bg-white border-gray-200 px-2 sm:px-4 py-2.5 rounded dark:bg-gray-800">
                <div className="container flex flex-wrap justify-between items-center mx-auto">
                    <Link href='/'>
                        <a  className="flex items-center">
                            <img src={`${publicRuntimeConfig.staticFolder}/LW_ERIC_Logo.png`} className="mr-3 h-6 h-14" alt="LifeWatch Logo" />
                        </a>
                    </Link>
                    <div className="flex items-center md:order-2">
                        <div className="relative inline-block text-left">
                            {status == "authenticated" ? (
                                <Menu>
                                    {({ open }) => (
                                        <>
                                            <Menu.Button className="inline-flex justify-center w-full">
                                                <img src={`${publicRuntimeConfig.staticFolder}/user_placeholder.jpeg`} className='h-10 rounded-full border border-slate-300' />
                                            </Menu.Button>

                                            <Transition
                                                show={open}
                                                enter="transition ease-out duration-100"
                                                enterFrom="transform opacity-0 scale-95"
                                                enterTo="transform opacity-100 scale-100"
                                                leave="transition ease-in duration-75"
                                                leaveFrom="transform opacity-100 scale-100"
                                                leaveTo="transform opacity-0 scale-95"
                                            >
                                                <Menu.Items
                                                    static
                                                    className="absolute right-0 w-56 mt-2 origin-top-right bg-white border border-gray-200 divide-y divide-gray-100 rounded-md shadow-lg outline-none"
                                                >
                                                    <div className="px-4 py-3 bg-orange-100">
                                                        <p className="text-sm font-medium leading-5 text-gray-900 truncate">
                                                            {session?.user?.name}
                                                        </p>
                                                    </div>
                                                    <div className="py-1">
                                                        <Menu.Item key={"signout"}>
                                                            {({ active }) => (
                                                                <a onClick={() => signOut()}
                                                                    href="#"
                                                                    className={`${active
                                                                        ? "bg-gray-100 text-gray-900"
                                                                        : "text-gray-700"
                                                                        } flex justify-between w-full px-4 py-2 text-sm leading-5 text-left`}
                                                                >
                                                                    Sign out
                                                                </a>
                                                            )}
                                                        </Menu.Item>
                                                    </div>
                                                </Menu.Items>
                                            </Transition>
                                        </>
                                    )}
                                </Menu>
                            ) : (
                                <div>
                                    <button onClick={() => signIn()} className="bg-blue-300 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded">
                                        Sign In
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                    {status == "authenticated" ? (
                        <div className="hidden justify-between items-center w-full md:flex md:w-auto md:order-1" id="mobile-menu-2">
                            <ul className="flex flex-col mt-4 md:flex-row md:space-x-8 md:mt-0 md:text-sm md:font-medium">
                            </ul>
                        </div>
                    ) : (
                        <div></div>
                    )}
                </div>
            </nav>
        </header>
    );
}

export { Nav };