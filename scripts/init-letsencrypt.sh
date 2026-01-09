#!/bin/bash

# SSL certificate initialization script for Excel2Markdown
# Run this script once on initial server setup

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Check required variables
if [ -z "$DOMAIN" ]; then
    echo "Error: DOMAIN is not set in .env file"
    exit 1
fi

if [ -z "$CERTBOT_EMAIL" ]; then
    echo "Error: CERTBOT_EMAIL is not set in .env file"
    exit 1
fi

echo "Initializing SSL certificate for domain: $DOMAIN"

# Create required directories
mkdir -p ./certbot/conf
mkdir -p ./certbot/www

# Download recommended TLS parameters
if [ ! -f "./certbot/conf/options-ssl-nginx.conf" ]; then
    echo "Downloading recommended TLS parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "./certbot/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "./certbot/conf/ssl-dhparams.pem"
fi

# Create dummy certificate for nginx to start
echo "Creating dummy certificate..."
mkdir -p "./certbot/conf/live/$DOMAIN"
openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout "./certbot/conf/live/$DOMAIN/privkey.pem" \
    -out "./certbot/conf/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=localhost"

# Update nginx config with actual domain
echo "Updating nginx configuration..."
sed -i "s/DOMAIN/$DOMAIN/g" docker/nginx/nginx.prod.conf

# Start nginx with dummy certificate
echo "Starting nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to start
sleep 5

# Delete dummy certificate
echo "Deleting dummy certificate..."
rm -rf "./certbot/conf/live/$DOMAIN"

# Request real certificate
echo "Requesting Let's Encrypt certificate..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $CERTBOT_EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# Reload nginx with real certificate
echo "Reloading nginx..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo ""
echo "SSL certificate initialized successfully!"
echo "You can now start all services with:"
echo "  docker-compose -f docker-compose.prod.yml up -d"
