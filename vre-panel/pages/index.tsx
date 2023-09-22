import {useContext, useEffect, useState} from 'react';
import getConfig from 'next/config';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown'

import {NewVREDialog} from '../components/NewVREDialog';
import {PaasConfigContext} from '../context/PaasConfig';
import PageLayout from "../components/PageLayout";

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
    <PageLayout>

      <div className="rounded shadow-lg bg-surface p-8">
        <h1 className="text-2xl text-onSurface mb-8">
          {paasConfigLoading ? (
            <span className="animate-pulse">
                  <span
                    className="inline-block min-h-[1em] w-3/12 flex-auto cursor-wait bg-onSurface align-middle opacity-50"></span>
                </span>
          ) : (
            paasConfig.title
          )}
        </h1>
        <p className="text-l text-onSurface">
          {paasConfigLoading ? (
            <span className="animate-pulse">
                  <span
                    className="inline-block min-h-[1em] w-full flex-auto cursor-wait bg-onSurface align-middle opacity-50"></span>
                </span>
          ) : (
            <div className="prose">
              <ReactMarkdown>{paasConfig.description}</ReactMarkdown>
            </div>
          )}
        </p>
        {paasConfigLoading || (
          paasConfig.documentation_url && (
            <p className="mt-4">
              <a
                href={paasConfig.documentation_url}
                className="text-primary hover:underline"
              >
                Documentation
              </a>
            </p>
          )
        )}
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>

        {vlabsLoading ? (
          <div className="rounded overflow-hidden shadow-lg bg-surface animate">
            <div>
              <img className="w-35 h-30 object-cover" src={`${publicRuntimeConfig.staticFolder}/HP-VRES.png`}/>
              <div className="font-bold text-l mb-2 bg-primaryMuted text-onPrimary p-5">
                <p className="animate-pulse">
                      <span
                        className="inline-block min-h-[1em] w-6/12 flex-auto cursor-wait bg-onPrimary align-middle opacity-50"></span>
                </p>
              </div>
              <div className="px-3 py-2">
                <p className="text-base truncate animate-pulse ...">
                      <span
                        className="inline-block min-h-[0.6em] w-6/12 flex-auto cursor-wait bg-onSurface align-middle opacity-50"></span>
                </p>
              </div>
            </div>
          </div>
        ) : (
          vlabs.length > 0 ? (
            vlabs.map((vlab: any) => {
              return (
                <div key={getSlug(vlab.title)} className="rounded overflow-hidden shadow-lg bg-surface">
                  <Link
                    href={{
                      pathname: '/vlabs/[slug]',
                      query: {slug: vlab.slug}
                    }}
                  >
                    <div>
                      <img className="w-35 h-30 object-cover"
                           src={`${publicRuntimeConfig.staticFolder}/HP-VRES.png`}/>
                      <div className="font-bold text-l mb-2 bg-primary text-onPrimary p-5">{vlab.title}</div>
                      <div className="px-3 py-2">
                        <p className="text-onSurface line-clamp-2">
                          {vlab.description}
                        </p>
                      </div>
                    </div>
                  </Link>
                </div>
              );
            })
          ) : (
            <div className="rounded overflow-hidden shadow-lg bg-surface p-5">
              No virtual labs found
            </div>
          )
        )
        }
      </div>

      <NewVREDialog isOpen={isOpen} setIsOpen={setIsOpen}/>

    </PageLayout>
  )
};

export default VLabs;