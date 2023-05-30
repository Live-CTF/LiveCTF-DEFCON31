FROM nginx

COPY infrastructure/web-frontend/src /usr/share/nginx/html
COPY infrastructure/web-frontend/conf/nginx.conf /etc/nginx/nginx.conf
COPY infrastructure/web-frontend/conf/conf.d/default.conf /etc/nginx/conf.d/default.conf
