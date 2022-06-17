import { AppProps } from 'next/app';
import '../styles/globals.css';
import { SessionProvider } from "next-auth/react"
import { useState } from 'react';
import RefreshTokenHandler from './auth/refreshTokenHandler';

export default function App({ Component, pageProps: { session, ...pageProps }} : AppProps): JSX.Element {

  const [_interval, setInterval] = useState(0);

  return (
    <SessionProvider session={session}>
      <Component {...pageProps} />
      <RefreshTokenHandler setInterval={setInterval} />
    </SessionProvider>
  )
}
