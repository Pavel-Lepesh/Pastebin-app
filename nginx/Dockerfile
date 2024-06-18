FROM nginx:latest

WORKDIR /var/www/html

RUN apt-get update \
    && apt-get install -y nginx-module-njs

COPY nginx.conf /etc/nginx/nginx.conf
COPY sub_auth.js /etc/nginx/conf.d/sub_auth.js

CMD ["nginx", "-g", "daemon off;"]