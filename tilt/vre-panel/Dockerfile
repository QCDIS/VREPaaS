FROM node:19-alpine3.16

WORKDIR /app

ADD ./vre-panel/package.json ./
RUN npm install

ADD ./vre-panel .

RUN chmod +x -R .

EXPOSE 3000
CMD ["npm", "run", "dev"]



