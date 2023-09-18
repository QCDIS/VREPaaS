import React, {useEffect, useState} from "react";
import getConfig from "next/config";
import {JWT} from "next-auth/jwt";
import clsx from "clsx";


type Props = {
  slug: string | string[] | undefined,
  isAuthenticated: boolean,
  token: JWT,
}

const DataProducts: React.FC<Props> = ({slug, isAuthenticated, token}) => {

  const {publicRuntimeConfig} = getConfig()

  const [assets, setAssets] = useState([])
  const [loadingAssets, setLoadingAssets] = useState(false)

  const fetchAssets = async () => {

    setLoadingAssets(true);

    var requestOptions: RequestInit = {
      method: "GET",
      headers: {
        "Authorization": "Bearer: " + token.accessToken
      },
    };

    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    const res = await fetch(`${apiUrl}/dataprods?vlab_slug=${slug}`, requestOptions);
    setLoadingAssets(false);

    return res.json();
  }

  useEffect(() => {
    if (isAuthenticated) {
      Promise.all([
        fetchAssets().then(setAssets),
      ])
    }
  }, [isAuthenticated]);

  return (
    <div>
      <button type="button"
              className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded cursor-pointer"
              onClick={() => {
                fetchAssets().then(setAssets)
              }}>
        <svg xmlns="http://www.w3.org/2000/svg" className={clsx("h-5", "w-5", loadingAssets && "animate-spin")}
             viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd"
                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                clipRule="evenodd"/>
        </svg>
      </button>
      {assets.length > 0 ? (
        <table className="table-auto bg-white mt-5">
          <thead>
          <tr>
            <th className="bg-blue-200 border text-left px-4 py-2">Title</th>
            <th className="bg-blue-200 border text-left px-4 py-2">Description</th>
          </tr>
          </thead>
          <tbody>
          {assets.map((dataProduct) => {
            return (
              <tr key={dataProduct['uuid']} className="odd:bg-gray-100">
                <td className={"border py-2 px-4 text-left"}>
                  <a className="underline text-blue-600 hover:text-blue-800 visited:text-purple-600"
                     target="blank"
                     href={dataProduct['data_url']}>
                    {dataProduct['title']}
                  </a>
                </td>
                <td className={"border py-2 px-4 text-left"}>{dataProduct['description']}</td>
              </tr>
            )
          })}
          </tbody>
        </table>
      ) : (
        <p className="mt-5">There is nothing to display</p>
      )}
    </div>
  )
}

export default DataProducts
