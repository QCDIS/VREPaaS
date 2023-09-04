import { getToken } from "next-auth/jwt";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { Nav } from "../templates/Nav";
// import useAuth from "../auth/useAuth";
// import { signIn, useSession } from 'next-auth/react';
import getConfig from 'next/config';
import Link from 'next/link';
import { NewVREDialog } from '../components/NewVREDialog';
// import useAuth from './auth/useAuth';

const { publicRuntimeConfig } = getConfig()






const NewAssignment = () => {

    var state = {value: 'to do'};

    function handleChange(event) {
        state = {value: event.target.value};
      }

    function handleSubmit(event) {
        console.log("hi")
        const target = event.target;
        console.log(target)
        alert('A name was submitted: ' + state.value);
        event.preventDefault();
      }


    return (
        <div>
            <Nav />
            <form onSubmit={handleSubmit}>
                <label>
                Name:
                <input type="text" name = "Name" onChange={handleChange} />
                </label>
                <label>
                Description:
                <input type="text" name = "Description" onChange={handleChange} />
                </label>
                <input type="submit" value="Submit" />
            </form>
        </div>
        );

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

export default NewAssignment;

// export async function getServerSideProps(context:any) {

//     const { req } = context;
//     const secret = process.env.SECRET;
//     const token = await getToken({ req, secret });

//     return {
//         props: {
//             token: token
//         }
//     };
// }