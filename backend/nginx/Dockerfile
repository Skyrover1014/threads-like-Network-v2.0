FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/
RUN mkdir -p /var/cache/nginx && chown -R nginx:nginx /var/cache/nginx