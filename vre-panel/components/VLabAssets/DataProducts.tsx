import React, {useEffect, useState} from "react";
import getConfig from "next/config";
import clsx from "clsx";


type Props = {
  slug: string | string[] | undefined,
}

const DataProducts: React.FC<Props> = ({slug}) => {

  const {publicRuntimeConfig} = getConfig()

  const [assets, setAssets] = useState([])
  const [loadingAssets, setLoadingAssets] = useState(false)
  const [backendError, setBackendError] = useState(false)

  const fetchAssets = async () => {

    setLoadingAssets(true);

    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    const res = await fetch(`${apiUrl}/dataprods?vlab_slug=${slug}`);
    setLoadingAssets(false);

    try {
      const dat = await res.json()
      setAssets(dat)
    } catch (e) {
      console.log(e)
      setBackendError(true)
    }
  }

  useEffect(() => {
    if (slug) {
      Promise.all([fetchAssets()])
    }
  }, [slug]);

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
          "Could not fetch data products"
        ) : (
          `${assets.length} data product${assets.length != 1 ? "s": ""}`
        )}
      </p>      {assets.length > 0 && (
        <table className="table-auto bg-white mt-5">
          <thead>
          <tr>
            <th className="bg-primaryContainer border text-left px-4 py-2">Title</th>
            <th className="bg-primaryContainer border text-left px-4 py-2">Description</th>
          </tr>
          </thead>
          <tbody>
          {assets.map((dataProduct) => {
            return (
              <tr key={dataProduct['uuid']} className="odd:bg-surfaceContainer">
                <td className={"border py-2 px-4 text-left"}>
                  <a className="text-primary hover:underline"
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
      )}
    </div>
  )
}

export default DataProducts
