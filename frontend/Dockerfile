FROM node:20

RUN npm install -g @angular/cli

WORKDIR /usr/src/app

COPY flowboard/package*.json ./

RUN npm install

COPY flowboard/ ./

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "4200"]
