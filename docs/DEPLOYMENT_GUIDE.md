# Deployment Guide - Document QA Agent

Complete guide for deploying the Document QA Agent to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Security](#security)

## Prerequisites

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 2 GB
- Disk: 10 GB
- OS: Linux, macOS, or Windows with Docker

**Recommended**:
- CPU: 4+ cores
- RAM: 4+ GB
- Disk: 50+ GB
- OS: Linux (Ubuntu 20.04+, Debian 11+)

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 1.29+
- **Python**: 3.11+ (for local development)
- **Git**: 2.30+

### Installation

**Docker (Ubuntu/Debian)**:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (optional)
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/document-qa-agent.git
cd document-qa-agent

# Create .env file from example
cp .env.example .env

# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop containers
docker-compose down
```

### Development Workflow

**Running Tests**:
```bash
# Run all tests in container
docker-compose exec app pytest tests/

# Run with coverage
docker-compose exec app pytest tests/ --cov=claude_mcp_docqa_agent

# Run specific test file
docker-compose exec app pytest tests/test_end_to_end.py -v
```

**Accessing Application**:
```bash
# MCP Server is available at localhost:8000
# Access via MCP protocol or test tools

# Check logs
docker-compose logs app

# Connect to container shell
docker-compose exec app /bin/bash
```

**Modifying Code**:
- Edit code in your IDE
- Changes to mounted volumes are reflected immediately
- For package changes, rebuild: `docker-compose up --build`

## Docker Deployment

### Building the Image

```bash
# Build with default tag
docker build -t document-qa-agent:latest .

# Build with version tag
docker build -t document-qa-agent:7.0 .

# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.12 -t document-qa-agent:latest .

# View image info
docker images document-qa-agent
```

### Running Container

```bash
# Run with default settings
docker run -d \
  --name document-qa-agent \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/reports:/app/reports \
  document-qa-agent:latest

# Run with custom environment
docker run -d \
  --name document-qa-agent \
  -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  -e MAX_FILE_SIZE_MB=200 \
  -v $(pwd)/data:/app/data \
  document-qa-agent:latest

# Check container status
docker ps

# View logs
docker logs -f document-qa-agent

# Stop container
docker stop document-qa-agent
docker rm document-qa-agent
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Security review completed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Backup strategy established
- [ ] Monitoring set up
- [ ] Resource limits set
- [ ] Health checks verified
- [ ] Logging configured
- [ ] SSL/TLS configured (if applicable)

### Kubernetes Deployment

**Deployment Manifest** (`k8s-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: document-qa-agent
  labels:
    app: document-qa-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: document-qa-agent
  template:
    metadata:
      labels:
        app: document-qa-agent
    spec:
      containers:
      - name: app
        image: document-qa-agent:7.0
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database-url
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
          requests:
            cpu: "1"
            memory: "1Gi"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - import sys; sys.exit(0)
          initialDelaySeconds: 40
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - import sys; sys.exit(0)
          initialDelaySeconds: 10
          periodSeconds: 10
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: app-data
      - name: logs
        persistentVolumeClaim:
          claimName: app-logs
---
apiVersion: v1
kind: Service
metadata:
  name: document-qa-agent
spec:
  selector:
    app: document-qa-agent
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

**Deploy to Kubernetes**:
```bash
# Create namespace
kubectl create namespace document-qa

# Apply configuration
kubectl apply -f k8s-deployment.yaml -n document-qa

# Check status
kubectl get pods -n document-qa

# View logs
kubectl logs -f deployment/document-qa-agent -n document-qa

# Scale replicas
kubectl scale deployment document-qa-agent --replicas=5 -n document-qa
```

### Docker Swarm Deployment

```bash
# Initialize swarm (on manager node)
docker swarm init

# Create config
docker config create app-config .env

# Deploy service
docker service create \
  --name document-qa-agent \
  --publish 8000:8000 \
  --config source=app-config,target=/app/.env \
  --replicas 3 \
  --limit-cpu 2 \
  --limit-memory 2g \
  document-qa-agent:7.0

# Check service status
docker service ps document-qa-agent

# Scale service
docker service scale document-qa-agent=5

# View logs
docker service logs document-qa-agent
```

## Configuration

### Environment Variables

**Core Settings**:
```bash
# Database
DATABASE_URL=sqlite:///./data/docqa.db

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_DIR=./logs

# Processing
MAX_FILE_SIZE_MB=100
SUPPORTED_FORMATS=pdf,docx
SUPPORTED_LANGUAGES=de,zh_CN

# Language Detection
LANGUAGE_DETECTION_MIN_CONFIDENCE=0.7

# MCP Server
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000

# Reporting
ENABLE_PDF_REPORTS=true
ENABLE_HTML_REPORTS=true
ENABLE_JSON_REPORTS=true
REPORT_DIR=./reports

# Debug
DEBUG=false
```

### Production Configuration

**High Performance**:
```bash
LOG_LEVEL=WARNING
MAX_FILE_SIZE_MB=500
LANGUAGE_DETECTION_MIN_CONFIDENCE=0.8
DEBUG=false
```

**Security-First**:
```bash
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
LANGUAGE_DETECTION_MIN_CONFIDENCE=0.9
DEBUG=false
DATABASE_URL=postgresql://user:pass@db:5432/docqa
```

### Configuration Files

Create `config/production.yaml`:
```yaml
document_processing:
  supported_formats: ["pdf", "docx"]
  max_file_size_mb: 100

language_detection:
  min_confidence: 0.8

analysis:
  check_font_consistency: true
  check_heading_hierarchy: true
  check_german_conventions: true
  check_chinese_conventions: true

reporting:
  generate_json: true
  generate_html: true
  generate_pdf: true

quality:
  min_language_confidence: 0.8
  max_critical_issues: 5
  max_warning_issues: 25

logging:
  level: INFO
  console_output: true
  file_logging: true
  log_dir: /app/logs

performance:
  cache_results: true
  parallel_processing: true
  max_parallel_pages: 4
```

## Monitoring

### Health Checks

```bash
# Manual health check
docker-compose exec app python -c "import sys; sys.exit(0)"

# HTTP health endpoint (if implemented)
curl -f http://localhost:8000/health || exit 1
```

### Logging

```bash
# View application logs
docker-compose logs app

# View logs with timestamps
docker-compose logs -t app

# View last 100 lines
docker-compose logs --tail=100 app

# Follow logs in real-time
docker-compose logs -f app
```

### Resource Monitoring

```bash
# Monitor container resources
docker stats document-qa-agent

# Check disk usage
docker exec document-qa-agent du -sh /app/data /app/logs /app/reports

# Monitor log file size
du -sh ./logs/
du -sh ./reports/
```

## Troubleshooting

### Common Issues

**Container won't start**:
```bash
# Check logs
docker-compose logs app

# Verify image
docker images document-qa-agent

# Rebuild image
docker-compose up --build
```

**Permission denied errors**:
```bash
# Check file ownership
ls -la ./data ./logs ./reports

# Fix permissions
chmod -R 755 ./data ./logs ./reports

# Or use correct user ID
docker-compose exec app id
```

**Out of memory**:
```bash
# Check limits
docker stats

# Increase in docker-compose.yml:
# memory: 4G
# Or restart with limits:
docker-compose down
docker-compose up -d
```

**Database locked**:
```bash
# Restart to reset database
docker-compose down
docker-compose up -d

# Or remove database and let it reinitialize
rm data/docqa.db
docker-compose restart app
```

## Security

### Best Practices

1. **Never commit secrets**:
   ```bash
   # Use .env files (not in git)
   # Use environment variables
   # Use secret management systems
   ```

2. **Minimal base image**:
   - Using python:3.11-slim
   - Only necessary packages installed
   - Non-root user (appuser)

3. **Security scanning**:
   ```bash
   # Scan image for vulnerabilities
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
     aquasec/trivy image document-qa-agent:latest
   ```

4. **Network isolation**:
   - Use Docker networks
   - Restrict port exposure
   - Use firewalls

5. **Resource limits**:
   - CPU limits: 2 cores
   - Memory limits: 2 GB
   - Disk quotas

### SSL/TLS Configuration

For HTTPS support, use a reverse proxy (nginx):

```nginx
upstream app {
    server app:8000;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs app`
2. Verify configuration: Check `.env` and `config/`
3. Test connectivity: `docker-compose exec app python -c "import claude_mcp_docqa_agent; print('OK')"`
4. Review documentation: See `docs/` directory

---

**Version**: 7.0  
**Last Updated**: 2026-09-28  
**Status**: Production Ready
