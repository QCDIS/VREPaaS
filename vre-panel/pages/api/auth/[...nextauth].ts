import axios from "axios";
import NextAuth from "next-auth"
import { JWT } from "next-auth/jwt";
import KeycloakProvider from "next-auth/providers/keycloak"
import type { NextApiRequest, NextApiResponse } from 'next'

import getConfig from 'next/config'

const { publicRuntimeConfig } = getConfig()

const refreshAccessToken = async (token: JWT) => {
	try {
		// Get a new set of tokens with a refreshToken
		const tokenResponse = await axios.post(
			process.env.KEYCLOAK_ISSUER + '/protocol/openid-connect/token',
			{
				grant_type: 'urn:ietf:params:oauth:grant-type:token-exchange',
				subject_token: token.accessToken,
				client_id: process.env.KEYCLOAK_CLIENT_ID,
				requested_token_type: 'urn:ietf:params:oauth:token-type:refresh_token'
			},
			{
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}
		);

		// console.log(tokenResponse);

		return {
			...token,
			accessToken: tokenResponse.data.accessToken,
			accessTokenExpiry: tokenResponse.data.accessTokenExpiry,
			refreshToken: tokenResponse.data.refreshToken
		}
	} catch (error) {
		return {
			...token,
			error: "RefreshAccessTokenError",
		}
	}
};

export default (req : NextApiRequest, res: NextApiResponse) => {
	return NextAuth(req, res, {
		providers: [
			KeycloakProvider({
				clientId: process.env.AUTH0_ID,
				clientSecret: process.env.AUTH0_SECRET,
				issuer:  process.env.AUTH0_ISSUER,
			})
		],
		// The secret should be set to a reasonably long random string.
        // It is used to sign cookies and to sign and encrypt JSON Web Tokens, unless
        // a separate secret is defined explicitly for encrypting the JWT.
		secret:  process.env.SECRET,
		callbacks: {
			async jwt({ token, user, account }) {
				if (account && user) {
	
					token.accessToken = account.access_token;
					token.refreshToken = account.refresh_token;
					token.accessTokenExpiry = account.expires_at;
					token.user = user;
				}

				// console.log(token);
	
				const unixTimeZero = Date.parse('01 Jan 1970 00:00:00 GMT');
				const expiryDate = new Date();
				expiryDate.setTime(unixTimeZero)
				expiryDate.setSeconds(expiryDate.getSeconds() + token.accessTokenExpiry);
				const refreshElapse = Math.round(expiryDate.getTime() - Date.now());
	
				if (refreshElapse > 0) return token;
	
				return refreshAccessToken(token);
	
			},
			async session({ session, token }) {
				if (token) {
					session.user = token.user;
					session.error = token.error;
					session.accessToken = token.accessToken;
					session.accessTokenExpiry = token.accessTokenExpiry;
				}
				return session;
			},
		},
		pages: {
			signIn: `${publicRuntimeConfig.basePath}/auth/signin`
		}
	})
}