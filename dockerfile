FROM php:7.3-cli
MAINTAINER at-consulting
RUN apt update && apt install composer 
WORKDIR /app
COPY . /app



