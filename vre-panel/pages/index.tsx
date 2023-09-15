import {useEffect, useState, useContext} from 'react';
import getConfig from 'next/config';
import Link from 'next/link';

import {NewVREDialog} from '../components/NewVREDialog';
import {Nav} from '../templates/Nav';
import Footer from '../components/Footer';
import {PaasConfigContext} from '../context/PaasConfig';

const getSlug = (title: string) => {

  return title
    .toLowerCase()
    .replace(/ /g, '-')
    .replace(/[^\w-]+/g, '');
}

const VLabs = ({}) => {

  const {publicRuntimeConfig} = getConfig()

  const {paasConfig, paasConfigLoading} = useContext(PaasConfigContext)

  const [isOpen, setIsOpen] = useState(false);
  const [vlabs, setVlabs] = useState([]);
  const [vlabsLoading, setVlabsLoading] = useState(true);

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

  return (
    <div className="min-h-screen flex flex-col mx-auto bg-gradient-to-b from-sky-200 to-orange-300">
      <Nav/>
      <div className="grow">
        <div className="container mx-auto space-y-10 py-10">
          <div className="max-w-full rounded shadow-lg bg-white p-8">
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
            {paasConfigLoading || (
              paasConfig.documentation_url && (
                <p className="mt-4">
                  <a
                    href={paasConfig.documentation_url}
                    className="text-blue-800 hover:underline"
                  >
                    Documentation
                  </a>
                </p>
              )
            )}
          </div>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10'>
            {vlabsLoading ? (
              <div className="rounded overflow-hidden shadow-lg bg-white animate">
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
                      <div key={getSlug(vlab.title)} className="rounded overflow-hidden shadow-lg bg-white">
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
                              <p className="text-gray-700 line-clamp-2">
                                {vlab.description}
                              </p>
                            </div>
                          </div>
                        </Link>
                      </div>
                    );
                  })
                ) : (
                  <div className="rounded overflow-hidden shadow-lg bg-white">
                    No virtual labs found
                  </div>
                )
              )
            }
          </div>
          <NewVREDialog isOpen={isOpen} setIsOpen={setIsOpen}/>
        </div>
      </div>
      <Footer/>
    </div>
  )
};

export default VLabs;