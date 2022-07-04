FROM node:18

WORKDIR /code/frontend

COPY frontend/package*.json .

RUN npm install

EXPOSE 3000

CMD [ "npm", "start" ]