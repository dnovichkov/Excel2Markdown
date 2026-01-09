# Deployment Guide

This guide explains how to deploy Excel2Markdown to a production server using GitHub Actions and Docker.

## Architecture Overview

```
GitHub Actions (CI)          Production Server
+------------------+         +------------------+
| 1. Run tests     |         |                  |
| 2. Build images  |   -->   | docker-compose   |
| 3. Push to GHCR  |         | pull & restart   |
+------------------+         +------------------+
        |                            |
        v                            v
+------------------+         +------------------+
| ghcr.io          |         | Nginx (443)      |
| - app:latest     |         | Certbot (SSL)    |
| - celery:latest  |         | FastAPI (8000)   |
| - nginx:latest   |         | Celery + Redis   |
+------------------+         +------------------+
```

## Prerequisites

- GitHub repository with Actions enabled
- Production server with Docker and Docker Compose installed
- Domain name pointing to your server's IP address

## Step 1: GitHub Repository Setup

### 1.1 Enable GitHub Container Registry

GitHub Container Registry (ghcr.io) is enabled by default. Your images will be published to:
- `ghcr.io/dnovichkov/excel2markdown/app`
- `ghcr.io/dnovichkov/excel2markdown/celery`
- `ghcr.io/dnovichkov/excel2markdown/nginx`

### 1.2 Push to GitHub

```bash
git add .
git commit -m "Add CI/CD configuration"
git push origin master
```

GitHub Actions will automatically:
1. Run tests
2. Build Docker images
3. Push to GitHub Container Registry

Check the Actions tab in your repository to monitor the build.

## Step 2: Server Setup

### 2.1 Install Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2.2 Clone Repository

```bash
git clone https://github.com/dnovichkov/Excel2Markdown.git
cd Excel2Markdown
```

### 2.3 Configure Environment

```bash
# Copy production environment template
cp .env.prod.example .env

# Edit configuration
nano .env
```

Update these values in `.env`:
```
DOMAIN=excel2md.yourdomain.com
CERTBOT_EMAIL=your-email@example.com
```

### 2.4 Update Nginx Config with Your Domain

```bash
# Replace DOMAIN placeholder with your actual domain
sed -i "s/DOMAIN/excel2md.yourdomain.com/g" docker/nginx/nginx.prod.conf
```

### 2.5 Login to GitHub Container Registry

Create a Personal Access Token (PAT) at https://github.com/settings/tokens with `read:packages` scope.

```bash
# Login to GHCR
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u dnovichkov --password-stdin
```

## Step 3: SSL Certificate Setup

### 3.1 Initialize Let's Encrypt Certificate

```bash
# Make script executable
chmod +x scripts/init-letsencrypt.sh

# Run initialization (requires domain to point to server)
./scripts/init-letsencrypt.sh
```

This script will:
1. Create a temporary self-signed certificate
2. Start Nginx
3. Request a real certificate from Let's Encrypt
4. Configure automatic renewal

## Step 4: Start Services

```bash
# Pull images and start all services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Updating the Application

When you push changes to the `master` branch:

1. GitHub Actions automatically builds and pushes new images
2. SSH to your server and run:

```bash
cd Excel2Markdown
./scripts/deploy.sh
```

Or manually:
```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f app
docker-compose -f docker-compose.prod.yml logs -f celery-worker
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Check Service Health

```bash
# Service status
docker-compose -f docker-compose.prod.yml ps

# Health check
curl -k https://your-domain.com/health
```

### Resource Usage

```bash
docker stats
```

## Troubleshooting

### SSL Certificate Issues

```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml run --rm certbot certificates

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal

# Reload nginx after renewal
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs app

# Rebuild if needed
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### Permission Issues

```bash
# Fix storage permissions
sudo chown -R 1000:1000 storage/
```

## Backup

### Backup Data

```bash
# Backup storage directory
tar -czf backup-$(date +%Y%m%d).tar.gz storage/

# Backup Redis data
docker-compose -f docker-compose.prod.yml exec redis redis-cli BGSAVE
```

### Restore

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore storage
tar -xzf backup-YYYYMMDD.tar.gz

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## Security Recommendations

1. **Firewall**: Only expose ports 80 and 443
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Updates**: Keep Docker and system packages updated
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Secrets**: Never commit `.env` file to repository

4. **Monitoring**: Consider adding monitoring (Prometheus, Grafana) for production use
