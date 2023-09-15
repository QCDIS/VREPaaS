import {getToken} from "next-auth/jwt";
import {useRouter} from "next/router";
import {Nav} from "../../templates/Nav";
import useAuth from "../auth/useAuth";
import dynamic from "next/dynamic";
import Footer from "../../components/Footer";
import VLabDescription from "../../components/VLabDescription";
import VLabWorkflowRuns from "../../components/VLabWorkflowRuns";
import VLabDataProducts from "../../components/VLabDataProducts";

const CatalogMapView = dynamic(() => import("../../components/catalog_map"), {ssr: false})

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
        <div className="container mx-auto py-10 grid grid-flow-row-dense grid-cols-4 grid-rows-5 gap-4">
          <div className="row-span-2 col-span-2 shadow-lg bg-white p-10">
            <VLabDescription slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </div>
          <div className="row-span-2 col-span-2 shadow-lg bg-white p-10">
            <VLabWorkflowRuns slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </div>
          <div className="row-span-2 col-span-2 shadow-lg bg-white p-10">
            <VLabDataProducts slug={slug} isAuthenticated={isAuthenticated} token={token}/>
          </div>
          <div className="row-span-2 col-span-2 shadow-lg bg-white p-10">
            <CatalogMapView vlab_slug={slug}/>
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