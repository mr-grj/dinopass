FROM node:18

ENV APP_USER=dinopass
ENV APP_HOME=/home/$APP_USER
ENV SRC_FOLDER=$APP_HOME/frontend

WORKDIR $SRC_FOLDER

COPY frontend/package*.json ./

RUN npm install

EXPOSE 3000

CMD [ "npm", "start" ]
