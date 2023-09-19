import Link from 'next/link';
import { Menu, Transition } from '@headlessui/react';
import { useSession, signIn, signOut } from "next-auth/react"
import getConfig from 'next/config'
import {useContext} from "react";
import {PaasConfigContext} from "../context/PaasConfig";


const Nav = () => {

    const { publicRuntimeConfig } = getConfig()
    const { data: session, status } = useSession()

    const {paasConfig, paasConfigLoading} = useContext(PaasConfigContext)

    return (
        <header className="top-0 z-30 w-full px-2 py-4 bg-surface sm:px-4 shadow-lg">
            <nav className="bg-surface border-gray-200 h-10 px-2 sm:px-4 rounded">
                <div className="container flex flex-wrap justify-between items-center mx-auto">
                    <Link href='/' className="flex items-center">
                        {paasConfigLoading || (
                            <img
                                src={paasConfig.site_icon}
                                alt="Site icon"
                                className="object-contain h-10 w-20"
                            />
                          )}
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
                                                    className="absolute right-0 w-56 mt-2 origin-top-right bg-surface border border-gray-200 divide-y divide-gray-100 rounded-md shadow-lg outline-none"
                                                >
                                                    <div className="px-4 py-3 bg-primary text-onPrimary">
                                                        <p className="text-sm font-medium leading-5 truncate">
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
                                    <button onClick={() => signIn()} className="bg-primary hover:bg-primaryDark text-onPrimary font-bold py-2 px-4 rounded">
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