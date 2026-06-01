# QERA Production Deployment Guide

## Phase 5: Production Readiness

### 1. Pre-Deployment Checklist

- [ ] All tests passing (run `npm test` for frontend, `pytest` for backend)
- [ ] Code review completed
- [ ] Security audit completed
- [ ] Database migrations tested on staging
- [ ] Environment variables configured for production
- [ ] SSL/TLS certificates obtained
- [ ] Monitoring and alerting configured
- [ ] Backup strategy documented and tested

### 2. Environment Setup

#### Backend Configuration

1. Copy environment template:
```bash
cp qera/backend/.env.example qera/backend/.env.production
```

2. Update `qera/backend/.env.production` with production values:
   - `JWT_SECRET_KEY`: Generate strong 512-bit key
   - `AI_SERVICE_PROVIDER`: Set to 'openai' if using OpenAI API
   - `OPENAI_API_KEY`: Add your API key
   - `CORS_ORIGINS`: Set to your domain
   - `DATABASE_PATH`: Use managed database or absolute path

3. Update `docker-compose.yml` with production secrets via Docker secrets or environment files

#### Frontend Configuration

1. Update `qera/frontend/.env.production`:
```
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
```

### 3. Docker Deployment

#### Build Images

```bash
# Build backend image
docker build -f Dockerfile -t qera-backend:latest .

# Build frontend image
docker build -f qera/frontend/Dockerfile.frontend -t qera-frontend:latest .
```

#### Run with Docker Compose

```bash
# Development
docker-compose up -d

# Production (use environment file)
docker-compose --env-file .env.production up -d
```

#### Push to Registry

```bash
docker tag qera-backend:latest your-registry/qera-backend:latest
docker tag qera-frontend:latest your-registry/qera-frontend:latest

docker push your-registry/qera-backend:latest
docker push your-registry/qera-frontend:latest
```

### 4. Database Setup

#### Run Migrations

```bash
# In backend container
cd /app/backend
python database_init.py
```

#### Initial Data

```bash
# Load seed data (if needed)
sqlite3 /app/database/qera.db < /app/database/seeds/dev_seed.sql
```

### 5. Reverse Proxy Configuration

#### Nginx Example

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 6. Health Checks

#### Backend Health

```bash
curl https://yourdomain.com/api/v1/health
# Response: {"status":"ok","message":"QERA backend is running"}
```

#### Frontend Health

```bash
curl https://yourdomain.com/
# Response: HTML homepage
```

### 7. Logging and Monitoring

#### Logs Location

- Backend: `/app/logs/qera.log`
- Frontend: Docker container stdout
- Nginx: `/var/log/nginx/access.log` and `error.log`

#### Configure Log Aggregation

1. Sentry (Error Tracking):
   - Set `SENTRY_DSN` in environment
   - Monitor error rates and performance

2. ELK Stack (Log Aggregation):
   - Ship logs to Elasticsearch
   - Use Kibana for visualization

3. Prometheus (Metrics):
   - Add Prometheus exporter middleware
   - Monitor request rates, latency, errors

### 8. Scaling

#### Horizontal Scaling

```yaml
# docker-compose.yml - Backend scaling
services:
  backend:
    # ... configuration ...
    deploy:
      replicas: 3
```

#### Load Balancing

Use HAProxy or Nginx upstream for multiple backend instances:

```nginx
upstream backend_cluster {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    least_conn;
}
```

### 9. Backup Strategy

#### Database Backup

```bash
# Daily automated backup (cron job)
0 2 * * * sqlite3 /app/database/qera.db ".backup /app/backups/qera_$(date +\%Y\%m\%d).db"

# Keep last 30 days
find /app/backups -name "qera_*.db" -mtime +30 -delete
```

#### Restore Backup

```bash
sqlite3 /app/database/qera.db ".restore /app/backups/qera_YYYYMMDD.db"
```

### 10. Security Hardening

#### Backend Security

- [ ] Enable HTTPS/TLS (enforce in code with `HTTPS_ONLY=true`)
- [ ] Set secure CORS headers
- [ ] Implement rate limiting (configured in `rate_limit.py`)
- [ ] Use strong JWT secret key (min 512 bits)
- [ ] Enable CSRF protection
- [ ] Sanitize all user inputs
- [ ] Keep dependencies updated (`pip list --outdated`)

#### Frontend Security

- [ ] Use HTTPS only
- [ ] Enable Content Security Policy (CSP)
- [ ] Set X-Frame-Options header
- [ ] Use secure cookie settings
- [ ] Keep dependencies updated (`npm audit`)
- [ ] Implement subresource integrity (SRI)

#### Infrastructure Security

- [ ] Firewall rules (only allow needed ports)
- [ ] Regular security audits
- [ ] SSL/TLS certificate renewal
- [ ] Secrets management (use HashiCorp Vault or similar)
- [ ] Regular backups and disaster recovery tests

### 11. Performance Optimization

#### Backend Optimization

- Enable async database operations (already implemented with SQLite async)
- Add database indexes for frequent queries
- Implement caching layer (Redis)
- Use CDN for static assets

#### Frontend Optimization

- [ ] Minify and compress assets
- [ ] Enable code splitting
- [ ] Use lazy loading for routes
- [ ] Implement service workers for offline support
- [ ] Optimize images and fonts

### 12. Monitoring Alerts

Create alerts for:
- Backend response time > 1 second
- Error rate > 1%
- Database size growth > threshold
- Disk space < 10%
- Memory usage > 80%
- CPU usage > 80%

### 13. CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci-cd.yml`) handles:
- Automated tests on push/PR
- Docker image building and pushing
- Production deployment on merge to main

### 14. Troubleshooting

#### Backend Won't Start

```bash
# Check logs
docker logs qera_backend

# Verify database
sqlite3 /app/database/qera.db ".tables"

# Check environment variables
docker exec qera_backend env
```

#### Frontend Not Loading

```bash
# Check frontend logs
docker logs qera_frontend

# Verify API connectivity
docker exec qera_backend curl http://localhost:8000/api/v1/health
```

#### Database Issues

```bash
# Check database integrity
sqlite3 /app/database/qera.db "PRAGMA integrity_check;"

# Backup and restore
sqlite3 /app/database/qera.db ".backup /tmp/qera_backup.db"
```

### 15. Support and Maintenance

- Document all deployment steps
- Set up on-call rotation for monitoring
- Schedule regular security audits
- Plan for database maintenance (VACUUM, ANALYZE)
- Keep an up-to-date runbook for incidents
