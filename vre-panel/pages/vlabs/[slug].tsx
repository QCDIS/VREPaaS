import {getToken} from "next-auth/jwt";
import {useRouter} from "next/router";
import {Nav} from "../../templates/Nav";
import useAuth from "../auth/useAuth";
import Footer from "../../components/Footer";
import VLabDescription from "../../components/VLabDescription";
import React from "react";
import VLAbAssets from "../../components/VLAbAssets";


interface VLabDetailsProps {
  token?: any;
}

const VLabDetails: React.FC<VLabDetailsProps> = ({token}) => {

  const isAuthenticated = useAuth(true);
  const router = useRouter();
  const {slug} = router.query;

  return (
    <div className="min-h-screen flex flex-col mx-auto bg-gradient-to-b from-sky-200 to-orange-300">
      <Nav/>
      <div className="grow">
        <div className="container mx-auto py-10 space-y-4 gap-4">
          <div className="rounded shadow-lg bg-white p-8">
            <VLabDescription slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </div>
          <div className="rounded shadow-lg bg-white p-8">
            <VLAbAssets slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </div>
        </div>
      </div>
      <Footer/>
    </div>
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