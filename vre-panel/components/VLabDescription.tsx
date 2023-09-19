import React, {useEffect, useState} from "react";
import getConfig from "next/config";
import {JWT} from "next-auth/jwt";

type Props = {
  slug: string | string[] | undefined,
  isAuthenticated: boolean,
  token: JWT,
}

const VLabDescription: React.FC<Props> = ({slug, isAuthenticated, token}) => {

  const {publicRuntimeConfig} = getConfig()

  const vlabPlaceholder = {
    title: "Loading ..",
    slug: "",
    description: "Loading ..",
    endpoint: ""
  }

  const [vlab, setVlab] = useState(vlabPlaceholder)
  const [backendError, setBackendError] = useState(false)

  const fetchVlab = async () => {

    var requestOptions: RequestInit = {
      method: "GET",
      headers: {
        "Authorization": "Bearer: " + token.accessToken
      },
    };

    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    const res = await fetch(`${apiUrl}/vlabs/${slug}`, requestOptions);
    try {
      const dat = await res.json()
      setVlab(dat)
    } catch (e) {
      console.log(e)
      setBackendError(true)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      Promise.all([fetchVlab()])
    }
  }, [isAuthenticated]);

  return (
    <div>
      {backendError ? (
        <p className="my-5">
          Could not load vlab description
        </p>
      ) : (
        <>
          <p className="text-4xl font-sans">{vlab.title}</p>
          <a target="blank" href={vlab.endpoint}>
            <button className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded mt-5">
              Launch
            </button>
          </a>
          <p className="mt-5 text-justify">{vlab.description}</p>
        </>
      )}
    </div>
  )
}

export default VLabDescription