import React, {useEffect, useState} from "react";
import getConfig from "next/config";
import {JWT} from "next-auth/jwt";
import clsx from "clsx";


type Props = {
  slug: string | string[] | undefined,
  isAuthenticated: boolean,
  token: JWT,
}

const WorkflowRuns: React.FC<Props> = ({slug, isAuthenticated, token}) => {

  const {publicRuntimeConfig} = getConfig()

  const [assets, setAssets] = useState([])
  const [loadingAssets, setLoadingAssets] = useState(false)
  const [backendError, setBackendError] = useState(false)

  const fetchAssets = async () => {

    setLoadingAssets(true);

    var requestOptions: RequestInit = {
      method: "GET",
      headers: {
        "Authorization": "Bearer: " + token.accessToken
      },
    };

    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    const res = await fetch(`${apiUrl}/workflows?vlab_slug=${slug}`, requestOptions);
    setLoadingAssets(false);

    try {
      const dat = await res.json()
      setAssets(dat)
    }
    catch (e) {
      console.log(e)
      setBackendError(true)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      Promise.all([fetchAssets()])
    }
  }, [isAuthenticated]);

  return (
    <div>
      <button type="button"
              className="bg-primary hover:bg-primaryDark text-white font-bold py-2 px-4 rounded cursor-pointer"
              onClick={() => Promise.all([fetchAssets()])}>
        <svg xmlns="http://www.w3.org/2000/svg" className={clsx("h-5", "w-5", loadingAssets && "animate-spin")}
             viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd"
                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                clipRule="evenodd"/>
        </svg>
      </button>
      <p className="my-5">
        {backendError ? (
          "Could not fetch workflows"
        ) : (
          `${assets.length} workflow run${assets.length != 1 ? "s": ""}`
        )}
      </p>
      {assets.length > 0 && (
        <table className="table-auto bg-white mt-5">
          <thead>
          <tr>
            <th className="bg-primaryContainer border text-left px-4 py-2">Name</th>
            <th className="bg-primaryContainer border text-left px-4 py-2">Status</th>
            <th className="bg-primaryContainer border text-left px-4 py-2">Progress</th>
          </tr>
          </thead>
          {slug != null ? (
            <tbody>
            {assets.map((workflow) => {
              return (
                <tr key={workflow['argo_id']} className="odd:bg-surfaceContainer">
                  <td className={"border text-left py-2 px-4"}>
                    {/*<a className="text-primary hover:underline"*/}
                    {/*   target="blank"*/}
                    {/*   href={workflow['argo_url']}>*/}
                    {/*  {workflow['argo_id']}*/}
                    {/*</a>*/}
                    {workflow['argo_id']}
                  </td>
                  <td className={"border py-2 px-4 text-left"}>{workflow['status']}</td>
                  <td className={"border py-2 px-4 text-left"}>{workflow['progress']}</td>
                </tr>
              )
            })}
            </tbody>
          ) : (
            <tbody>
            </tbody>
          )}
        </table>
      )}
    </div>
  )
}

export default WorkflowRuns
