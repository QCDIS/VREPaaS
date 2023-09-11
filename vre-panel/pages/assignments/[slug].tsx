import { getToken } from "next-auth/jwt";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { Nav } from "../../templates/Nav";
import { signOut, useSession } from "next-auth/react";
// import useAuth from "../auth/useAuth";
// import { signIn, useSession } from 'next-auth/react';
import getConfig from 'next/config';
import Link from 'next/link';
import { NewVREDialog } from '../components/NewVREDialog';
// import useAuth from './auth/useAuth';
import dotenv from  'dotenv'
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
    const StudentPlaceholder = {
        keycloak_ID: "Loading ..",
        name: "",
        assignments_enrolled: "",
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
    const [Stud, setStud] = useState(StudentPlaceholder)
    const [vlab, setVlab] = useState(vlabPlaceholder)
    var [isEnrolled, setEnrolled] = useState(false)
    const session = useSession();
    var userName = "none";
 
    
    try {
        userName = session.data.user.name;
    }
    catch{
        console.log("session trouble")
    }
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
                })
                .catch((error) => {
                    console.log('Featching error:'+error)
                });

        const url2 = new URL("http://localhost:8000/api/students/");
        if (userName != "none"){
            console.log("session trouble resolved")
            fetch(`${url2}${userName}`)
                .then((res) => res.json())
                .then((data) => {
                    setStud(data)
                })
                .catch((error) => {
                    console.log('Featching error:'+error)
                });
                if (Stud.assignments_enrolled === null){
                    setEnrolled(false)
                    Stud.assignments_enrolled = "";
                    
                }
                else{
                    if(Stud.assignments_enrolled.includes(`${slug}`)){
                        setEnrolled(true)
                    }
                }
            }
    }, []);
       

    
    
    function enrollButton() {
        setEnrolled(true)
        if (userName != "none"){
            const url = 'http://localhost:8000/api/students/'
            const data = {
                assignments_enrolled:`${Stud.assignments_enrolled};${slug}` ,
                keycloak_ID: userName,
                name: userName,
            };
            console.log(JSON.stringify(data));
            fetch(`${url}${userName}/`, {
                method: "PUT",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
            });
        }
        Stud.assignments_enrolled =`${Stud.assignments_enrolled};${slug}`
    }

    function unEnrollButton() {
        setEnrolled(false)
        if (userName != "none"){
            const url = 'http://localhost:8000/api/students/'
            Stud.assignments_enrolled = Stud.assignments_enrolled.replace(`;${slug}`,"")
            var assignments_enrolled = Stud.assignments_enrolled;
            if (Stud.assignments_enrolled ==="") assignments_enrolled = ".";
            const data = {
                assignments_enrolled:`${assignments_enrolled}` ,
                keycloak_ID: userName,
            };
            Stud.assignments_enrolled =assignments_enrolled;
            console.log(JSON.stringify(data));
            fetch(`${url}${userName}/`, {
                method: "PUT",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
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
                    { !isEnrolled ?<a target="blank">
                        <button style={{float: 'right'}} className="bg-blue-400 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded mt-5" onClick={enrollButton}>
                            Enroll
                        </button>
                    </a>: null}
                    {isEnrolled ?<a target="blank">
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
