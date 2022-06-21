FROM node:16-alpine3.14

WORKDIR /app

ADD ./vre-panel/package.json ./vre-panel/package-lock.json ./
RUN npm install

ADD ./vre-panel .

EXPOSE 3000
CMD ["npm", "run", "dev"]