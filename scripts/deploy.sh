#!/bin/bash

# Deployment script for Excel2Markdown
# Run this script to pull latest images and restart services

set -e

echo "Deploying Excel2Markdown..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Login to GitHub Container Registry
echo "Logging in to GitHub Container Registry..."
echo $GHCR_TOKEN | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin

# Pull latest images
echo "Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Restart services with zero downtime
echo "Restarting services..."
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Clean up old images
echo "Cleaning up old images..."
docker image prune -f

# Show status
echo ""
echo "Deployment complete! Service status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "View logs with: docker-compose -f docker-compose.prod.yml logs -f"
