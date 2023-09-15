import React, {useEffect, useState} from "react";
import getConfig from "next/config";
import {JWT} from "next-auth/jwt";
import clsx from "clsx";


type Props = {
  slug: string | string[] | undefined,
  isAuthenticated: boolean,
  token: JWT,
}

const VLabDescription: React.FC<Props> = ({slug, isAuthenticated, token}) => {

  const {publicRuntimeConfig} = getConfig()

  const [workflows, setWorkflows] = useState([])
  const [loadingWorkflow, setLoadingWorkflows] = useState(false)

  const fetchWorkflows = async () => {

    setLoadingWorkflows(true);

    var requestOptions: RequestInit = {
      method: "GET",
      headers: {
        "Authorization": "Bearer: " + token.accessToken
      },
    };

    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    const res = await fetch(`${apiUrl}/workflows?vlab_slug=${slug}`, requestOptions);
    setLoadingWorkflows(false);

    return res.json();
  }

  useEffect(() => {
    if (isAuthenticated) {
      Promise.all([
        fetchWorkflows().then(setWorkflows),
      ])
    }
  }, [isAuthenticated]);

  return (
    <div>
      <p className="text-2xl font-sans">Workflows Runs</p>
      <button type="button"
              className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded mt-5 cursor-pointer"
              onClick={() => {
                fetchWorkflows().then(setWorkflows)
              }}>
        <svg xmlns="http://www.w3.org/2000/svg" className={clsx("h-5", "w-5", loadingWorkflow && "animate-spin")}
             viewBox="0 0 20 20"
             fill="currentColor">
          <path fillRule="evenodd"
                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                clipRule="evenodd"/>
        </svg>
      </button>
      <table className="table-auto bg-white mt-5">
        <thead>
        <tr>
          <th className="bg-blue-200 border text-left px-8 py-4">Name</th>
          <th className="bg-blue-200 border text-left px-8 py-4">Status</th>
          <th className="bg-blue-200 border text-left px-8 py-4">Progress</th>
        </tr>
        </thead>
        {slug != null ? (
          <tbody>
          {workflows.map((workflow) => {
            return (
              <tr key={workflow['argo_id']} className="odd:bg-gray-100">
                <td className={"border py-2 px-4"}>
                  <a className="underline text-blue-600 hover:text-blue-800 visited:text-purple-600"
                     target="blank"
                     href={workflow['argo_url']}>
                    {workflow['argo_id']}
                  </a>
                </td>
                <td className={"border py-2 px-4 text-center"}>{workflow['status']}</td>
                <td className={"border py-2 px-4 text-center"}>{workflow['progress']}</td>
              </tr>
            )
          })}
          </tbody>
        ) : (
          <tbody>
          </tbody>
        )}
      </table>
    </div>
  )
}

export default VLabDescription
