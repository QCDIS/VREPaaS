import NextAuth from "next-auth"
import { JWT } from "next-auth/jwt";
import KeycloakProvider from "next-auth/providers/keycloak"

const refreshAccessToken = async (token: JWT) => {
  try {

  } catch (error) {
    console.log(error);
  }
};

export default NextAuth({
  providers: [
    KeycloakProvider({
      clientId: "paas",
      clientSecret: "62ac41ad-474b-4c15-abc0-a8350f987198",
      issuer: "https://lifewatch.lab.uvalight.net:32443/auth/realms/ess-22",
    })
  ],
  secret: process.env.SECRET,
  callbacks: {
    async jwt({ token, user, account }) {
      if (account && user) {

        console.log(account);
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
        token.accessTokenExpiry = account.expires_at;
        token.user = user;
      }

      const unixTimeZero = Date.parse('01 Jan 1970 00:00:00 GMT');
      const expiryDate = new Date();
      expiryDate.setTime(unixTimeZero)
      expiryDate.setSeconds(expiryDate.getSeconds() + token.accessTokenExpiry);
      const refreshElapse = Math.round(expiryDate.getTime() - Date.now());
      console.log(refreshElapse);

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
    signIn: "/auth/signin"
  }
})