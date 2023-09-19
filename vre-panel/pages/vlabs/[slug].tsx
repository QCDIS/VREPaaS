import {getToken} from "next-auth/jwt";
import {useRouter} from "next/router";
import VLabDescription from "../../components/VLabDescription";
import React from "react";
import VLAbAssets from "../../components/VLAbAssets";
import PageLayout from "../../components/PageLayout";
import useAuth from "../auth/useAuth";


interface VLabDetailsProps {
  token?: any;
}

const VLabDetails: React.FC<VLabDetailsProps> = ({token}) => {

  const isAuthenticated = useAuth(true);
  const router = useRouter();
  const {slug} = router.query;

  return (
    <PageLayout>

        <div className="rounded shadow-lg bg-white p-8">
          <VLabDescription slug={slug} isAuthenticated={isAuthenticated} token={token}/>
        </div>

        <div className="rounded shadow-lg bg-white p-8">
          <VLAbAssets slug={slug} isAuthenticated={isAuthenticated} token={token}/>
        </div>

    </PageLayout>
  )
}

export default VLabDetails;

export async function getServerSideProps(context: any) {

  const {req} = context;
  const secret = process.env.SECRET;
  const token = await getToken({req, secret});
  console.log(token)
  return {
    props: {
      token: token
    }
  };
}