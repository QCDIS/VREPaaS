import { AppProps } from 'next/app';
import '../styles/globals.css';
import { SessionProvider } from "next-auth/react"
import { useState } from 'react';
import getConfig from 'next/config'

export default function App({ Component, pageProps: { session, ...pageProps }} : AppProps): JSX.Element {

  const { publicRuntimeConfig } = getConfig()
  const [interval, setInterval] = useState(0);

  return (
    <SessionProvider session={session} refetchInterval={interval} basePath={`${publicRuntimeConfig.basePath}/api/auth`}>
      <Component {...pageProps} />
    </SessionProvider>
  )
}
