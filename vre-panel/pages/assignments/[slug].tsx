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
        endpoint: "",
        vlab_slug: "",
        long_description: ""
    }
    const StudentPlaceholder = {
        keycloak_ID: "Loading ..",
        name: "",
        assignments_enrolled: "",
    }
    // const isAuthenticated = useAuth(true);
    const router = useRouter();
    const { slug } = router.query;
    const [Ass, setAss] = useState(AssPlaceholder)
    const [Stud, setStud] = useState(StudentPlaceholder)
    const keycloak_ID = "vre-paas-latife-dag"
      
    const url = new URL("http://localhost:8000/api/assignments/");
        
    fetch(`${url}${slug}`)
        .then((res) => res.json())
        .then((data) => {
            setAss(data)
        })
        .catch((error) => {
            console.log('Featching error:'+error)
        });

    const url2 = new URL("http://localhost:8000/api/students/");
    
    fetch(`${url2}${keycloak_ID}`)
        .then((res) => res.json())
        .then((data) => {
            setStud(data)
        })
        .catch((error) => {
            console.log('Featching error:'+error)
        });
    
    var isEnrolled = false;
    if (Stud.assignments_enrolled === null){
        isEnrolled = false;
        Stud.assignments_enrolled = "";
    }
    else{
        if(Stud.assignments_enrolled.includes(`${slug}`)){
            isEnrolled=true;
        }
    }
    function enrollButton() {
        isEnrolled = true;
        let name = prompt("Please enter your name:", "Harry Potter");
        if (name == null || name == "") {
            console.log("User cancelled the prompt.");
          } else {
            console.log("Name: " + name);
          }
    const url = 'http://localhost:8000/api/students/'
    const data = {
        assignments_enrolled:`${Stud.assignments_enrolled};${slug}` ,
        keycloak_ID: keycloak_ID,
        name: name,
    };
    console.log(JSON.stringify(data));
    fetch(`${url}${keycloak_ID}/`, {
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

    function unEnrollButton() {
        isEnrolled = false;
        const url = 'http://localhost:8000/api/students/'
        Stud.assignments_enrolled = Stud.assignments_enrolled.replace(`;${slug}`,"")
        var assignments_enrolled = Stud.assignments_enrolled;
        if (Stud.assignments_enrolled ==="") assignments_enrolled = ".";
        const data = {
            assignments_enrolled:`${assignments_enrolled}` ,
            keycloak_ID: keycloak_ID,
        };
        console.log(JSON.stringify(data));
        fetch(`${url}${keycloak_ID}/`, {
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

    


    return (
        <div>
            <Nav />
            <div className="grid grid-flow-row-dense grid-cols-1 grid-rows-1 gap-4 p-5 min-h-screen mx-auto bg-gradient-to-b from-sky-100 to-orange-300">
                <div className="row-span-4 col-span-2 shadow-lg bg-white p-10">
                    <p className="text-4xl font-sans">{Ass.title}</p>
                    <a target="blank" href= {'../vlabs/' + Ass.vlab_slug}>
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
