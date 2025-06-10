# 🐳 Docker Quick Start Guide

This is a quick start guide for running the AWS IAM Generator using Docker. For comprehensive deployment instructions including Kubernetes, AWS ECS, monitoring, and production considerations, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📋 Prerequisites

- **Docker** (20.10 or later)
- **Docker Compose** (2.0 or later)
- **4GB RAM** minimum
- **2GB disk space** for images and data

## 🚀 Quick Start

### Option 1: Using the Docker Manager Script (Recommended)

```bash
# Make the script executable (if not already)
chmod +x docker-manager.sh

# Build and start production environment
./docker-manager.sh start

# Or start development environment with hot reloading 🔥
./docker-manager.sh dev
```

### Option 2: Using Docker Compose Directly

```bash
# Production environment
docker-compose up -d

# Development environment with hot reload 🔥
docker-compose -f docker-compose.dev.yml up -d
```

## 🔥 Development Environment Features

The development setup includes advanced hot reload capabilities:

- **Backend Hot Reload**: Automatic Python code reloading with uvicorn `--reload`
- **Frontend Hot Reload**: Vite HMR (Hot Module Replacement) for instant updates
- **Volume Mounts**: Live code editing without container rebuilds
  - `./backend/app:/app/app`
  - `./backend/iam_generator:/app/iam_generator`
  - `./tests:/app/tests`
- **Debug Logging**: Enhanced logging for development troubleshooting

## 🌐 Access Points

Once running, you can access:

- **Frontend Web UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Available Commands

The `docker-manager.sh` script provides convenient commands:

| Command | Description |
|---------|-------------|
| `./docker-manager.sh build` | Build Docker images |
| `./docker-manager.sh start` | Start production environment |
| `./docker-manager.sh dev` | Start development environment |
| `./docker-manager.sh stop` | Stop all services |
| `./docker-manager.sh restart` | Restart services |
| `./docker-manager.sh status` | Show service status |
| `./docker-manager.sh logs [service]` | Show logs |
| `./docker-manager.sh cli [args...]` | Run CLI commands |
| `./docker-manager.sh test` | Run test suite |
| `./docker-manager.sh health` | Check service health |
| `./docker-manager.sh cleanup` | Clean up resources |

## 📝 CLI Usage in Docker

You can run CLI commands directly in Docker containers:

```bash
# Using the manager script
./docker-manager.sh cli analyze s3 list-buckets
./docker-manager.sh cli generate-role ec2 describe-instances

# Using Docker directly
docker run --rm -it iam-generator-backend:latest cli analyze s3 list-buckets
```

## 🛠️ Development Environment

The development environment includes:

- **Hot reloading** for both frontend and backend
- **Source code mounting** for real-time changes
- **Debug logging** enabled
- **Development tools** pre-installed

```bash
# Start development environment
./docker-manager.sh dev

# View development logs
./docker-manager.sh logs

# Run tests
./docker-manager.sh test
```

## 📊 Monitoring and Debugging

### View Service Status
```bash
./docker-manager.sh status
```

### View Logs
```bash
# All services
./docker-manager.sh logs

# Specific service
./docker-manager.sh logs backend
./docker-manager.sh logs frontend
```

### Health Checks
```bash
# Automated health check
./docker-manager.sh health

# Manual health checks
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## 💾 Data Persistence

The application uses Docker volumes for data persistence:

- **Application data**: `./data` directory
- **Application logs**: `./logs` directory
- **Database**: Stored in `data/` directory

These directories are automatically created and mounted to containers.

## ⚙️ Configuration

### Environment Variables

You can customize the deployment using environment variables:

```bash
# Backend configuration
export PORT=8000
export LOG_LEVEL=info
export PYTHONPATH=/app/src

# Start with custom configuration
PORT=9000 LOG_LEVEL=debug ./docker-manager.sh start
```

### AWS Credentials

For local development, you can mount AWS credentials:

```bash
# Uncomment the volume mount in docker-compose.yml
# - ~/.aws:/home/appuser/.aws:ro
```

⚠️ **Security Note**: Never include AWS credentials in Docker images for production!

## 🔒 Security Considerations

- **Non-root user**: Containers run as non-root user `appuser`
- **Security headers**: Frontend includes security headers
- **Network isolation**: Services communicate through internal Docker network
- **Minimal images**: Multi-stage builds for smaller attack surface
- **Health checks**: Regular health monitoring enabled

## 🚢 Production Deployment

### Building for Production

```bash
# Build optimized production images
./docker-manager.sh build

# Start production environment
./docker-manager.sh start
```

### Resource Requirements

For production deployment:

- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4 CPU cores, 8GB RAM
- **Storage**: 10GB for application and logs

### Scaling

To scale the backend service:

```bash
docker-compose up -d --scale backend=3
```

### Load Balancing

For production load balancing, consider:

- **Nginx/Apache** reverse proxy
- **AWS Application Load Balancer**
- **Kubernetes** for orchestration

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests in container
./docker-manager.sh test

# Run specific test categories
docker run --rm iam-generator-backend:latest test -k "test_analyzer"
```

### Integration Testing

```bash
# Test API endpoints
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"command": "s3 list-buckets"}'

# Test batch analysis
curl -X POST http://localhost:8000/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{"commands": ["s3 list-buckets", "ec2 describe-instances"]}'
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
./docker-manager.sh restart
```

### Cleaning Up

```bash
# Remove unused containers, images, and volumes
./docker-manager.sh cleanup

# Complete cleanup (use with caution)
docker system prune -a --volumes
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Docker not running**: Start Docker Desktop/daemon
3. **Build failures**: Check Docker logs and network connectivity
4. **Memory issues**: Increase Docker memory allocation

### Debug Commands

```bash
# Check container logs
docker logs iam-generator-backend
docker logs iam-generator-frontend

# Access container shell
docker exec -it iam-generator-backend bash

# Check resource usage
docker stats
```

### Getting Help

```bash
# Show detailed help
./docker-manager.sh help

# Check service health
./docker-manager.sh health

# View service status
./docker-manager.sh status
```

## 📁 File Structure

```
├── Dockerfile                 # Backend container definition
├── Dockerfile.frontend        # Frontend container definition
├── docker-compose.yml         # Production orchestration
├── docker-compose.dev.yml     # Development orchestration
├── docker-entrypoint.sh       # Container entrypoint script
├── docker-manager.sh          # Management script
├── nginx.conf                 # Frontend web server config
├── .dockerignore              # Files to exclude from build
└── data/                      # Persistent application data
└── logs/                      # Application logs
```

## 🎯 Best Practices

1. **Use the manager script** for consistent operations
2. **Monitor resource usage** with `docker stats`
3. **Regular backups** of the `data/` directory
4. **Update dependencies** regularly
5. **Review logs** for security and performance insights
6. **Use development mode** for coding and testing
7. **Production mode** for stable deployments

## 📚 Additional Resources

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide including Kubernetes, AWS ECS, monitoring, and production considerations
- **[README.md](README.md)** - Main project documentation
- **Frontend Guide** - [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)

For production deployments, security considerations, monitoring setup, and advanced configurations, please refer to the comprehensive [DEPLOYMENT.md](DEPLOYMENT.md) guide.

---

For more information, see the main [README.md](README.md) or run `./docker-manager.sh help`.
