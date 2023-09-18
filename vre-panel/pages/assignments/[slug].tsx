import { getToken } from "next-auth/jwt";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { Nav } from "../../templates/Nav";
import { signOut, useSession } from "next-auth/react";
import getConfig from 'next/config';
const { publicRuntimeConfig } = getConfig()


interface AssDetailsProps {
    token?: any;
  }




const AssDetails: React.FC<AssDetailsProps> = ({ token  }) => {

    const AssPlaceholder = {
        title: "Loading ..",
        slug: "",
        description: "Loading ..",
        vlab : 0,
        long_description: ""
    }
    const vlabPlaceholder = {
        title: "Loading ..",
        slug: "",
        description: "Loading ..",
        endpoint: ""
    }
    
    // const isAuthenticated = useAuth(true);
    const router = useRouter();
    const { slug } = router.query;
    const [Ass, setAss] = useState(AssPlaceholder)
    const [vlab, setVlab] = useState(vlabPlaceholder)
    var [isEnrolled, setEnrolled] = useState(false)
    const session = useSession();
    var userName = "none";
 

    const url = new URL("http://localhost:8000/api/assignments/");
    useEffect(() => {
        fetch(`${url}${slug}`)
            .then((res) => res.json())
            .then((data) => {
                setAss(data)
                console.log(data);
                setVlab(data.vlab);
                })
                .catch((error) => {
                    console.log('Featching error:'+error)
                });
        

        if (session.status=='authenticated'){
            userName = session.data.user.name;
            console.log("session trouble resolved")
            console.log(userName)
            const data2 = {
                slug: slug,
                student_id: userName,
                type:'view'
            };
            fetch(`${url}${slug}/`, {
                method: "PATCH", 
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data2)
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                if (typeof data == "boolean")
                    setEnrolled(data);

            });
            }
    }, [session]);
       

    function tryToGetUserName(){
        if (session.status=='authenticated'){
            return session.data.user.name
        }
        return "none"
    }

    
    function enrollButton() {
        userName = tryToGetUserName();
        if (userName != "none"){
            const data2 = {
                slug: slug,
                student_id: userName,
                type:'enroll'
            };
            console.log(JSON.stringify(data2));
            fetch(`${url}${slug}/`, {
                method: "PATCH", 
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data2)
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                if (data=='added')
                    setEnrolled(true);
            });
        }
    }   

    function unEnrollButton() {
        userName = tryToGetUserName();
        if (userName != "none"){
            const data2 = {
                slug: slug,
                student_id: userName,
                type:'un-enroll'
            };
            console.log(JSON.stringify(data2));
            fetch(`${url}${slug}/`, {
                method: "PATCH", 
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data2)
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                if (data=='removed')
                    setEnrolled(false);
            });
        }
    }

    
    return (
        <div>
            <Nav />
            <div className="grid grid-flow-row-dense grid-cols-1 grid-rows-1 gap-4 p-5 min-h-screen mx-auto bg-gradient-to-b from-sky-100 to-orange-300">
                <div className="row-span-4 col-span-2 shadow-lg bg-white p-10">
                    <p className="text-4xl font-sans">{Ass.title}</p>
                    <a target="blank" href= {'../vlabs/' + vlab.slug}>
                        <button  className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded mt-5">
                            Go to Vlab
                        </button>
                    </a>
                    { !isEnrolled && session.status=='authenticated' ?<a target="blank">
                        <button style={{float: 'right'}} className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded mt-5" onClick={enrollButton}>
                            Enroll
                        </button>
                    </a>: null}
                    {isEnrolled && session.status=='authenticated' ?<a target="blank">
                        <button style={{float: 'right'}} className="bg-neutral-400 hover:bg-neutral-500 text-white font-bold py-2 px-4 rounded mt-5" onClick={unEnrollButton}>
                            Unenroll
                        </button>
                    </a>: null}
                    <div >{Ass.long_description}</div>
                </div>
                
            </div>
        </div>
    )

}

export async function getServerSideProps(context:any) {

    const { req } = context;
    const secret = process.env.SECRET;
    const token = await getToken({ req, secret });

    return {
        props: {
            token: token
        }
    };
}

export default AssDetails;
