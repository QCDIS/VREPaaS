import Link from 'next/link';
import {Menu, Transition} from '@headlessui/react';
import {useSession, signIn, signOut} from "next-auth/react"
import React, {Fragment, useContext} from "react";
import {PaasConfigContext} from "../context/PaasConfig";
import clsx from "clsx";
import {useRouter} from "next/router";


const Nav = () => {

  const menuPages = [
    {
      label: "Home",
      href: "/",
    },
    {
      label: "About",
      href: "/about",
    },
  ]

  const {data: session, status} = useSession()
  const router = useRouter()

  const {paasConfig, paasConfigLoading} = useContext(PaasConfigContext)

  return (
    <header className="top-0 z-30 w-full md:w-72 md:min-h-screen px-2 py-4 bg-surface sm:px-4 shadow-lg">
      <nav className="bg-surface border-gray-200 h-10 px-2 sm:px-4 rounded">
        <div className="container flex flex-row md:flex-col justify-between items-center md:items-start mx-auto">

          <Link href='/' className="flex items-center md:w-full">
            {paasConfigLoading || (
              <img
                src={paasConfig.site_icon}
                alt="Site icon"
                className="object-contain h-10 w-20 md:w-full md:h-auto md:p-4"
              />
            )}
          </Link>


          <ul
            className="hidden md:block font-bold space-y-2 pt-10"
          >
            {menuPages.map((page) => {
              return (
                <li key={page.href}>
                  <Link
                    href={page.href}
                    className={clsx(
                      page.href == router.pathname ? "text-primary" : "text-onSurface",
                      "hover:underline"
                    )}
                  >
                    {page.label}
                  </Link>
                </li>
              )
            })}
            <li className="pt-10 font-normal">
              {status == "authenticated" ? (
                <>
                  <p>Logged in as {session?.user?.name}</p>
                  <a onClick={() => signOut()} href="#" className="hover:underline">[Logout]</a>
                </>
              ) : (
                <a onClick={() => signIn()} href="#">Login</a>
              )}
            </li>
          </ul>

          <Menu as="div" className="md:hidden relative inline-block text-left">
            <div>
              <Menu.Button
                className="w-full rounded bg-primary hover:bg-primaryDark text-onPrimary px-4 py-2">
                <>
                  <svg xmlns="http://www.w3.org/2000/svg"
                       className="h-5 w-5"
                       viewBox="0 0 10 8" fill="currentColor"
                  >
                    <path
                      d='M1 1h8M1 4h 8M1 7h8'
                      stroke="currentColor"
                    />
                  </svg>
                </>

              </Menu.Button>
            </div>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items
                className="absolute right-0 md:left-0 mt-2 w-56 origin-top-right md:origin-top-left divide-y divide-gray-100 rounded bg-surface shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div className="px-1 py-1 ">
                  {menuPages.map((page) => {
                    return (
                      <Menu.Item key={page.href}>
                        {({active}) => (
                          <Link
                            href={page.href}
                            className={clsx(
                              page.href == router.pathname ? "text-primary" : "text-onSurface",
                              active ? 'bg-primary !text-onPrimary' : 'text-onSurface',
                              "group flex w-full items-center rounded px-2 py-2")}
                          >
                            {page.label}
                          </Link>
                        )}
                      </Menu.Item>
                    )
                  })}
                </div>
                <div className="px-1 py-1 ">
                  {status == "authenticated" && (
                    <div className="px-2 py-2 font-bold text-primary">
                      <p className="">
                        Logged in as {session?.user?.name}
                      </p>
                    </div>
                  )}
                  <Menu.Item>
                    {({active}) => (
                      <button
                        className={clsx(
                          active ? 'bg-primary text-onPrimary' : 'text-onSurface',
                          status == "authenticated" ? "px-6" : "px-2",
                          'group flex w-full items-center rounded py-2')}
                        onClick={() => {
                          status == "authenticated" ? signOut() : signIn()
                        }}
                      >
                        {status == "authenticated" ? "Logout" : "Login"}
                      </button>
                    )}
                  </Menu.Item>
                </div>
              </Menu.Items>
            </Transition>
          </Menu>

        </div>
      </nav>
    </header>
  );
}

export {Nav};