FROM nginx:1.25

COPY app/static /usr/share/nginx/html/static

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 81
