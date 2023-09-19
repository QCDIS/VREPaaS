import React, {ReactNode} from "react";

import {Nav} from "../templates/Nav";
import Footer from "./Footer";

interface Props {
  children: ReactNode,
}

const PageLayout = ({children} : Props) => {
  return (
    <div className="min-h-screen flex flex-col md:flex-row mx-auto bg-surfaceContainer">
      <Nav/>
      <div className="mx-auto w-full flex flex-col space-y-5 py-5 md:px-5">
        <main className="grow flex flex-col space-y-4">
          {children}
        </main>
        <Footer/>
      </div>
    </div>
  )
}

export default PageLayout
