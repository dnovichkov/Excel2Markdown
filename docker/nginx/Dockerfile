FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
