# Deployment Guide

This document provides comprehensive deployment instructions for the AWS CLI IAM Permissions Analyzer in various environments.

## Table of Contents

- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [AWS ECS Deployment](#aws-ecs-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 2GB RAM
- 1GB free disk space

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd iam_generator

# Start the application
docker-compose up -d

# Verify deployment
curl http://localhost:8000/health
curl http://localhost:3000

# View logs
docker-compose logs -f
```

### Production Configuration

#### docker-compose.yml Configuration

The production configuration includes:
- FastAPI backend (port 8000)
- React frontend with Nginx (port 3000)
- Health checks for both services
- Restart policies
- Volume mounts for logs

```yaml
version: '3.8'
services:
  backend:
    build: .
    container_name: iam-generator-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app/src
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: iam-generator-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Custom Environment Variables

Create a `.env` file for custom configuration:

```bash
# .env file
BACKEND_PORT=8000
FRONTEND_PORT=3000
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000"]
```

### Development Mode

For development with hot reload:

```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up

# Or build development images
docker build -f Dockerfile.dev -t iam-generator:dev .
```

### Managing the Deployment

```bash
# Stop services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d

# View resource usage
docker stats

# Clean up
docker-compose down -v
docker system prune -f
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster 1.20+
- kubectl configured
- At least 2 worker nodes
- 4GB RAM and 2 CPU cores available

### Deployment Manifests

#### Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: iam-generator
  labels:
    name: iam-generator
```

#### Backend Deployment

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iam-generator-backend
  namespace: iam-generator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: iam-generator-backend
  template:
    metadata:
      labels:
        app: iam-generator-backend
    spec:
      containers:
      - name: backend
        image: iam-generator:latest
        ports:
        - containerPort: 8000
        env:
        - name: PYTHONPATH
          value: "/app/src"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Frontend Deployment

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iam-generator-frontend
  namespace: iam-generator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: iam-generator-frontend
  template:
    metadata:
      labels:
        app: iam-generator-frontend
    spec:
      containers:
      - name: frontend
        image: iam-generator-frontend:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
```

#### Services

```yaml
# services.yaml
apiVersion: v1
kind: Service
metadata:
  name: iam-generator-backend-service
  namespace: iam-generator
spec:
  selector:
    app: iam-generator-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: iam-generator-frontend-service
  namespace: iam-generator
spec:
  selector:
    app: iam-generator-frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
```

#### Ingress (Optional)

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: iam-generator-ingress
  namespace: iam-generator
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: iam-generator.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: iam-generator-frontend-service
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: iam-generator-backend-service
            port:
              number: 8000
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f services.yaml
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get pods -n iam-generator
kubectl get services -n iam-generator

# View logs
kubectl logs -f deployment/iam-generator-backend -n iam-generator
kubectl logs -f deployment/iam-generator-frontend -n iam-generator
```

## AWS ECS Deployment

### Prerequisites

- AWS CLI configured
- ECS cluster created
- ECR repositories created
- VPC with subnets and security groups

### Task Definition

```json
{
  "family": "iam-generator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/iam-generator-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PYTHONPATH",
          "value": "/app/src"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/iam-generator",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "backend"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    },
    {
      "name": "frontend",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/iam-generator-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "dependsOn": [
        {
          "containerName": "backend",
          "condition": "HEALTHY"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/iam-generator",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "frontend"
        }
      }
    }
  ]
}
```

### Service Definition

```bash
# Create ECS service
aws ecs create-service \
  --cluster iam-generator-cluster \
  --service-name iam-generator-service \
  --task-definition iam-generator:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-abcdef],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-west-2:ACCOUNT:targetgroup/iam-gen-tg/1234567890123456,containerName=frontend,containerPort=3000"
```

### Application Load Balancer

```bash
# Create target groups
aws elbv2 create-target-group \
  --name iam-generator-frontend-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-12345678 \
  --target-type ip \
  --health-check-path /

aws elbv2 create-target-group \
  --name iam-generator-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345678 \
  --target-type ip \
  --health-check-path /health

# Create load balancer
aws elbv2 create-load-balancer \
  --name iam-generator-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-abcdef
```

## Environment Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PYTHONPATH` | Python module path | `/app/src` | Yes |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` | No |
| `API_PREFIX` | API URL prefix | `/api/v1` | No |
| `MAX_WORKERS` | Uvicorn worker count | `1` | No |

### Configuration Files

#### Production Settings

```python
# config/production.py
import os

# Server settings
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))
WORKERS = int(os.getenv("MAX_WORKERS", 1))

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://your-domain.com"
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Monitoring and Logging

### Health Checks

Both services include health check endpoints:

- Backend: `GET /health`
- Frontend: `GET /` (returns 200 for healthy nginx)

### Logging Configuration

#### Docker Logging

```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Centralized Logging with ELK Stack

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  filebeat:
    image: elastic/filebeat:7.15.0
    volumes:
      - ./logs:/var/log/app
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml
    depends_on:
      - elasticsearch

  elasticsearch:
    image: elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  kibana:
    image: kibana:7.15.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Monitoring with Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'iam-generator-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'iam-generator-frontend'
    static_configs:
      - targets: ['frontend:3000']
```

## Security Considerations

### Container Security

1. **Non-root user**: Both containers run as non-root users
2. **Read-only filesystem**: Consider mounting volumes as read-only where possible
3. **Resource limits**: Set appropriate CPU and memory limits
4. **Security scanning**: Regularly scan images for vulnerabilities

```dockerfile
# Security-hardened Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "backend_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Network Security

1. **HTTPS only**: Use TLS/SSL certificates in production
2. **CORS configuration**: Restrict CORS origins to known domains
3. **Rate limiting**: Implement rate limiting for API endpoints
4. **Firewall rules**: Restrict access to necessary ports only

### Data Security

1. **No sensitive data**: The application doesn't store AWS credentials
2. **Input validation**: All inputs are validated and sanitized
3. **Output sanitization**: Generated policies are validated before output

## Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Check container status
docker-compose ps

# Restart services
docker-compose restart
```

#### Frontend Can't Connect to Backend

1. Check that both containers are running
2. Verify network connectivity
3. Check CORS configuration
4. Verify API endpoint URLs

```bash
# Test backend connectivity from frontend container
docker-compose exec frontend curl http://backend:8000/health

# Test from host
curl http://localhost:8000/health
curl http://localhost:3000
```

#### High Memory Usage

```bash
# Monitor resource usage
docker stats

# Check for memory leaks in logs
docker-compose logs backend | grep -i memory
```

#### Slow Response Times

1. Check container resource limits
2. Monitor database query performance
3. Review application logs for bottlenecks

```bash
# Monitor response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/analyze
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set debug environment
export LOG_LEVEL=DEBUG
docker-compose up -d

# Or modify docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG
  - PYTHONPATH=/app/src
```

### Performance Tuning

#### Backend Optimization

```python
# backend_server.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend_server:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Increase for better performance
        access_log=False,  # Disable for production
        loop="uvloop"  # Faster event loop
    )
```

#### Frontend Optimization

```nginx
# nginx.conf
worker_processes auto;
worker_connections 1024;

http {
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    upstream backend {
        server backend:8000;
        keepalive 32;
    }
}
```

## Backup and Recovery

### Data Backup

Since the application is stateless, backup focuses on:

1. **Configuration files**: docker-compose.yml, environment files
2. **Custom permissions database**: If modified
3. **Application logs**: For audit purposes

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup configuration
cp docker-compose.yml $BACKUP_DIR/
cp .env $BACKUP_DIR/

# Backup logs
tar -czf $BACKUP_DIR/logs.tar.gz logs/

# Backup custom data
tar -czf $BACKUP_DIR/data.tar.gz data/
```

### Disaster Recovery

```bash
# Restore from backup
RESTORE_DIR="/backup/20240609"

# Stop current services
docker-compose down

# Restore configuration
cp $RESTORE_DIR/docker-compose.yml .
cp $RESTORE_DIR/.env .

# Restore data
tar -xzf $RESTORE_DIR/data.tar.gz

# Start services
docker-compose up -d
```

## Maintenance

### Regular Maintenance Tasks

1. **Update container images**: Monthly security updates
2. **Log rotation**: Automatic log cleanup
3. **Resource monitoring**: Monitor CPU, memory, disk usage
4. **Security scanning**: Regular vulnerability scans

```bash
# Maintenance script
#!/bin/bash

# Update images
docker-compose pull

# Clean up old images
docker image prune -f

# Restart with latest images
docker-compose up -d

# Check health
sleep 30
curl -f http://localhost:8000/health
curl -f http://localhost:3000
```

### Scaling

#### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
  
  frontend:
    deploy:
      replicas: 2
```

```bash
# Scale services
docker-compose up -d --scale backend=3 --scale frontend=2
```

#### Load Balancing

Use nginx or a cloud load balancer to distribute traffic across multiple instances.

---

For additional support or questions, please refer to the project documentation or create an issue in the repository.
