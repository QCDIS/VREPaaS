import Link from 'next/link';
import { Menu, Transition } from '@headlessui/react';
import { useRouter } from 'next/router';
import { useSession, signIn, signOut } from "next-auth/react"
import useAuth from '../pages/auth/useAuth';
import getConfig from 'next/config'


const Nav = () => {

    const { publicRuntimeConfig } = getConfig()
    const { data: session, status } = useSession()
    const router = useRouter();
    const menu = [
        { key: 'home', label: 'Home', url: `${publicRuntimeConfig.basePath}/home` },
        { key: 'vlabs', label: 'Virtual Labs', url: `${publicRuntimeConfig.basePath}/vlabs` },
    ];

    return (
        <header className="sticky top-0 z-30 w-full px-2 py-4 bg-white sm:px-4 shadow-xl">
            <nav className="bg-white border-gray-200 px-2 sm:px-4 py-2.5 rounded dark:bg-gray-800">
                <div className="container flex flex-wrap justify-between items-center mx-auto">
                    <a href="/vreapp" className="flex items-center">
                        <img src={`${publicRuntimeConfig.staticFolder}/LW_ERIC_Logo.png`} className="mr-3 h-6 sm:h-10" alt="LifeWatch Logo" />
                    </a>
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
                                {menu.map((item) => (
                                    <li key={item.key}>
                                        <Link href={item.url}>
                                            <a href={item.url} className={`${router.asPath == item.url ? 'text-blue-700' : 'text-gray-700'} block py-2 pr-4 pl-3 border-b border-gray-100 hover:bg-gray-50 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 active:text-blue-700 md:p-0 dark:text-gray-400 md:dark:hover:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent dark:border-gray-700`} aria-current="page">
                                                {item.label}
                                            </a>
                                        </Link>
                                    </li>
                                ))}
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