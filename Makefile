# AWS IAM Generator - Docker Makefile
# Provides convenient shortcuts for Docker operations

.PHONY: help build start dev stop restart status logs test cli health cleanup

# Default target
help:
	@echo "AWS IAM Generator - Docker Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  build      Build Docker images"
	@echo "  start      Start production environment"
	@echo "  dev        Start development environment" 
	@echo "  stop       Stop all services"
	@echo "  restart    Restart services"
	@echo "  status     Show service status"
	@echo "  logs       Show service logs"
	@echo "  test       Run test suite"
	@echo "  cli        Run CLI interactively"
	@echo "  health     Check service health"
	@echo "  cleanup    Clean up resources"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make start"
	@echo "  make dev"
	@echo "  make logs"

# Build Docker images
build:
	@./docker-manager.sh build

# Start production environment
start: build
	@./docker-manager.sh start

# Start development environment
dev: build
	@./docker-manager.sh dev

# Stop all services
stop:
	@./docker-manager.sh stop

# Restart services
restart:
	@./docker-manager.sh restart

# Show service status
status:
	@./docker-manager.sh status

# Show logs
logs:
	@./docker-manager.sh logs

# Run tests
test:
	@./docker-manager.sh test

# Run CLI interactively
cli:
	@./docker-manager.sh cli

# Check health
health:
	@./docker-manager.sh health

# Clean up resources
cleanup:
	@./docker-manager.sh cleanup

# Development shortcuts
install: build
	@echo "✅ Docker images built and ready to use"
	@echo "Run 'make start' for production or 'make dev' for development"

# Run specific CLI commands
cli-analyze:
	@./docker-manager.sh cli analyze s3 list-buckets

cli-help:
	@./docker-manager.sh cli --help
