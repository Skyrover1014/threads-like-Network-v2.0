FROM nginx:alpine
RUN apk add --no-cache curl \
 && rm -f /etc/nginx/conf.d/default.conf 
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/
RUN mkdir -p /var/cache/nginx && chown -R nginx:nginx /var/cache/nginx