#!/bin/sh
sed  -i "s|NEXT_PUBLIC_ENV_VRE_API_URL=.*$|NEXT_PUBLIC_ENV_VRE_API_URL=${NEXT_PUBLIC_ENV_VRE_API_URL}|" .env
cat .env
 run build
node server.js