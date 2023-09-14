import {useEffect, useState, createContext, ReactNode} from "react";
import getConfig from "next/config";


export const PaasConfigContext = createContext({
  paasConfig: {
    title: "",
    description: "",
  },
  paasConfigLoading: true,
});

export function PaasConfigProvider({children,}: { children: ReactNode }) {
  const {publicRuntimeConfig} = getConfig()

  const [paasConfig, setPaasConfig] = useState({
    title: "Virtual Lab environments",
    description: "A collection of virtual lab environments",
  })
  const [paasConfigLoading, setPaasConfigLoading] = useState(true)

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
    <PaasConfigContext.Provider value={{paasConfig: paasConfig, paasConfigLoading: paasConfigLoading}}>
      {children}
    </PaasConfigContext.Provider>
  );
}
