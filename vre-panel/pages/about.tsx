import Link from 'next/link';
import getConfig from 'next/config'

import React from "react";
import PageLayout from "../components/PageLayout";

const About = ({}) => {

  const {publicRuntimeConfig} = getConfig()

  return (
    <PageLayout>

      <div className="rounded shadow-lg bg-white p-8">
        <h1 className="text-2xl text-gray-800 mb-8">
          About NaaVRE
        </h1>
        <p className="text-base text-gray-800">
          NaaVRE is built by LifeWatch ERIC VLIC and the QCDIS team at the University of Amsterdam.
        </p>

        <div className="flex flex-col sm:flex-row items-center mt-8">
          <Link href="https://www.lifewatch.eu/">
            <img
              alt="LifeWatch ERIC logo"
              src={`${publicRuntimeConfig.staticFolder}/logo-lifewatch-eric-medium.png`}
              width="150"
              className="m-10"
            />
          </Link>
          <Link href="https://www.uva.nl/en">
            <img
              alt="University of Amsterdam logo"
              src={`${publicRuntimeConfig.staticFolder}/logo-uva-medium.png`}
              width="170"
              className="m-10"
            />
          </Link>
        </div>
      </div>

    </PageLayout>
  )
};

export default About;
