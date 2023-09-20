import {useRouter} from "next/router";
import VLabDescription from "../../components/VLabDescription";
import React, {useEffect, useState} from "react";
import VLAbAssets from "../../components/VLAbAssets";
import PageLayout from "../../components/PageLayout";
import useAuth from "../auth/useAuth";
import VLabInstances from "../../components/VLabInstances";
import getConfig from "next/config";
import {VLab} from "../../types/vlab";

const VLabDetails = () => {

  const {publicRuntimeConfig} = getConfig()

  const vlabPlaceholder: VLab = {
    title: "Loading ..",
    slug: "",
    description: "Loading ..",
    endpoint: ""
  }

  useAuth(true);
  const router = useRouter();
  const {slug} = router.query;

  const [vlab, setVlab] = useState(vlabPlaceholder)
  const [backendError, setBackendError] = useState(false)

  const fetchVlab = async () => {
    const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
    const res = await fetch(`${apiUrl}/vlabs/${slug}`);
    try {
      const dat = await res.json()
      setVlab(dat)
    } catch (e) {
      console.log(e)
      setBackendError(true)
    }
  }

  useEffect(() => {
    if (slug) {
      Promise.all([fetchVlab()])
    }
  }, [slug]);


  return (
    <PageLayout>

      <div className="rounded shadow-lg bg-white p-8">
        <VLabDescription vlab={vlab} backendError={backendError}/>
      </div>

      <div className="rounded shadow-lg bg-white p-8">
        <VLabInstances vlab={vlab} slug={slug}/>
      </div>

      <div className="rounded shadow-lg bg-white p-8">
        <VLAbAssets slug={slug}/>
      </div>

    </PageLayout>
  )
}

export default VLabDetails;
