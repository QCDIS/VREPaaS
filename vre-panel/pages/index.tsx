import {useEffect, useState} from 'react';
import getConfig from 'next/config';
import Link from 'next/link';

import {NewVREDialog} from '../components/NewVREDialog';
import {Nav} from '../templates/Nav';

const getSlug = (title: string) => {

  return title
    .toLowerCase()
    .replace(/ /g, '-')
    .replace(/[^\w-]+/g, '');
}

const VLabs = () => {

  const {publicRuntimeConfig} = getConfig()

  const [isOpen, setIsOpen] = useState(false);
  const [vlabs, setVlabs] = useState([]);
  const [vlabsLoading, setVlabsLoading] = useState(true);

  const [paasConfig, setPaasConfig] = useState({
    title: "Virtual Lab environments",
    description: "A collection of virtual lab environments",
  })
  const [paasConfigLoading, setPaasConfigLoading] = useState(true)

  useEffect(() => {

    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    fetch(`${apiUrl}/vlabs`)
      .then((res) => res.json())
      .then((data) => {
        setVlabs(data);
        setVlabsLoading(false)
      })
      .catch((error) => {
        console.log(error)
        setVlabsLoading(false)
      });
  }, []);

  useEffect(() => {
    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    fetch(`${apiUrl}/paas_configuration`)
      .then((res) => res.json())
      .then((data) => {
        if (data.length > 0) {
          setPaasConfig(data[0]);
        }
        setPaasConfigLoading(false)
      })
      .catch((error) => {
        console.log(error)
        setPaasConfigLoading(false)
      });
  }, []);

  return (
    <div>
      <Nav/>
      <div className='min-h-screen mx-auto bg-gradient-to-b from-sky-100 to-orange-300 space-y-10 p-10'>
        <div className="max-w-full rounded bg-white p-8">
          <h1 className="text-2xl text-gray-800 mb-8">
            {paasConfigLoading ? (
              <span className="animate-pulse">
                <span className="inline-block min-h-[1em] w-3/12 flex-auto cursor-wait bg-current align-middle opacity-50"></span>
              </span>
            ) : (
              paasConfig.title
            )}
          </h1>
          <p className="text-l text-gray-800">
            {paasConfigLoading ? (
              <span className="animate-pulse">
                <span className="inline-block min-h-[1em] w-full flex-auto cursor-wait bg-current align-middle opacity-50"></span>
              </span>
            ) : (
              paasConfig.description
            )}
          </p>
        </div>
        <div className='flex flex-row space-x-10'>
          {vlabsLoading ? (
            <div className="w-1/3 rounded overflow-hidden shadow-lg bg-white animate">
              <div>
                <img className="w-35 h-30 object-cover" src={`${publicRuntimeConfig.staticFolder}/HP-VRES.png`}/>
                <div className="font-bold text-l mb-2 bg-gray-300 text-white p-5">
                  <p className="animate-pulse">
                    <span className="inline-block min-h-[1em] w-6/12 flex-auto cursor-wait bg-current align-middle opacity-50"></span>
                  </p>
                </div>
                <div className="px-3 py-2">
                  <p className="text-gray-700 text-base truncate animate-pulse ...">
                    <span className="inline-block min-h-[0.6em] w-6/12 flex-auto cursor-wait bg-current align-middle opacity-50"></span>
                  </p>
                </div>
              </div>
            </div>
            ) : (
              vlabs.length > 0 ? (
                vlabs.map((vlab: any) => {
                  return (
                    <div key={getSlug(vlab.title)} className="w-1/3 rounded overflow-hidden shadow-lg bg-white">
                      <Link
                        href={{
                          pathname: '/vlabs/[slug]',
                          query: {slug: vlab.slug}
                        }}
                      >
                        <div>
                          <img className="w-35 h-30 object-cover" src={`${publicRuntimeConfig.staticFolder}/HP-VRES.png`}/>
                          <div className="font-bold text-l mb-2 bg-blue-500 text-white p-5">{vlab.title}</div>
                          <div className="px-3 py-2">
                            <p className="text-gray-700 text-base truncate ...">
                              {vlab.description}
                            </p>
                          </div>
                        </div>
                      </Link>
                    </div>
                  );
                })
              ) : (
                <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-10 p-5 text-gray-700">
                  Could not load virtual found
                </div>
              )
            )
          }
        </div>
        <NewVREDialog isOpen={isOpen} setIsOpen={setIsOpen}/>
      </div>
    </div>
  )
};

export default VLabs;