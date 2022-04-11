FROM node:10.15.0-alpine

RUN apk add --no-cache bash

WORKDIR /usr/workspace

COPY package*.json ./

RUN /bin/bash -c 'npm ci --verbose'

COPY . ./

CMD ["npm", "start"]

EXPOSE 8080
LABEL Name="DCS Frontend" \
    VERSION="1.0.0"
