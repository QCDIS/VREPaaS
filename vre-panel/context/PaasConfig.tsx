import {useEffect, useState, createContext, ReactNode} from "react";
import getConfig from "next/config";


export const PaasConfigContext = createContext({
  paasConfig: {
    title: "",
    description: "",
    documentation_url: "",
    site_icon: "",
  },
  paasConfigLoading: true,
});

export function PaasConfigProvider({children,}: { children: ReactNode }) {
  const {publicRuntimeConfig} = getConfig()

  const [paasConfig, setPaasConfig] = useState({
    title: "Virtual Lab environments",
    description: "A collection of virtual lab environments",
    documentation_url: "https://github.com/QCDIS/NaaVRE/blob/main/README.md",
    site_icon: `${publicRuntimeConfig.staticFolder}/LW_ERIC_Logo.png`,
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
