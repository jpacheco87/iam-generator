#!/bin/bash

# AWS IAM Generator - Docker Management Script
# This script provides easy commands to build, run, and manage the containerized application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Use 'docker compose' if available, fallback to 'docker-compose'
    if docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi
}

# Function to build images
build_images() {
    print_header "Building Docker Images"
    
    print_status "Building backend image..."
    docker build -t iam-generator-backend:latest .
    
    print_status "Building frontend image..."
    docker build -f Dockerfile.frontend -t iam-generator-frontend:latest .
    
    print_status "Images built successfully!"
}

# Function to start production environment
start_production() {
    print_header "Starting Production Environment"
    
    # Create necessary directories
    mkdir -p data logs
    
    print_status "Starting services with Docker Compose..."
    $DOCKER_COMPOSE -f docker-compose.yml up -d
    
    print_status "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    check_services_health
    
    print_status "🚀 Application is running!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
}

# Function to start development environment
start_development() {
    print_header "Starting Development Environment"
    
    # Create necessary directories
    mkdir -p data logs
    
    print_status "Starting development services with Docker Compose..."
    $DOCKER_COMPOSE -f docker-compose.dev.yml up -d
    
    print_status "Development environment is starting..."
    print_status "Frontend (with hot reload): http://localhost:3000"
    print_status "Backend (with auto-reload): http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
}

# Function to check service health
check_services_health() {
    print_status "Checking service health..."
    
    # Check backend health
    for i in {1..30}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_status "✅ Backend is healthy"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "⚠️  Backend health check timeout"
        fi
        sleep 2
    done
    
    # Check frontend health
    for i in {1..30}; do
        if curl -f http://localhost:3000/health >/dev/null 2>&1; then
            print_status "✅ Frontend is healthy"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "⚠️  Frontend health check timeout"
        fi
        sleep 2
    done
}

# Function to stop services
stop_services() {
    print_header "Stopping Services"
    
    print_status "Stopping production services..."
    $DOCKER_COMPOSE -f docker-compose.yml down
    
    print_status "Stopping development services..."
    $DOCKER_COMPOSE -f docker-compose.dev.yml down
    
    print_status "Services stopped successfully!"
}

# Function to clean up everything
cleanup() {
    print_header "Cleaning Up"
    
    print_status "Stopping all services..."
    stop_services
    
    print_status "Removing containers..."
    docker container prune -f
    
    print_status "Removing unused images..."
    docker image prune -f
    
    print_status "Removing unused volumes..."
    docker volume prune -f
    
    print_status "Cleanup completed!"
}

# Function to run CLI commands
run_cli() {
    print_header "Running CLI Command"
    
    if [ $# -eq 0 ]; then
        print_status "Starting interactive CLI..."
        docker run --rm -it \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd)/logs:/app/logs" \
            iam-generator-backend:latest cli --help
    else
        print_status "Running CLI command: $*"
        docker run --rm -it \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd)/logs:/app/logs" \
            iam-generator-backend:latest cli "$@"
    fi
}

# Function to run tests
run_tests() {
    print_header "Running Tests"
    
    print_status "Building test image..."
    docker build -t iam-generator-test:latest .
    
    print_status "Running test suite..."
    docker run --rm \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        iam-generator-test:latest test
}

# Function to show logs
show_logs() {
    print_header "Service Logs"
    
    if [ -n "$1" ]; then
        print_status "Showing logs for service: $1"
        $DOCKER_COMPOSE -f docker-compose.yml logs -f "$1"
    else
        print_status "Showing logs for all services..."
        $DOCKER_COMPOSE -f docker-compose.yml logs -f
    fi
}

# Function to show status
show_status() {
    print_header "Service Status"
    
    print_status "Docker Compose Status:"
    $DOCKER_COMPOSE -f docker-compose.yml ps
    
    print_status "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Function to show help
show_help() {
    echo "AWS IAM Generator - Docker Management Script"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  build               Build Docker images"
    echo "  start|up           Start production environment"
    echo "  dev                Start development environment"
    echo "  stop|down          Stop all services"
    echo "  restart            Restart services"
    echo "  status             Show service status"
    echo "  logs [service]     Show logs (optionally for specific service)"
    echo "  cli [args...]      Run CLI commands"
    echo "  test               Run test suite"
    echo "  health             Check service health"
    echo "  cleanup            Stop services and clean up resources"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build                                    # Build images"
    echo "  $0 start                                    # Start production"
    echo "  $0 dev                                      # Start development"
    echo "  $0 cli analyze s3 list-buckets             # Run CLI command"
    echo "  $0 logs backend                            # Show backend logs"
    echo "  $0 test                                     # Run tests"
}

# Main script logic
main() {
    check_docker
    check_docker_compose
    
    case "${1:-help}" in
        "build")
            build_images
            ;;
        "start"|"up")
            build_images
            start_production
            ;;
        "dev"|"development")
            build_images
            start_development
            ;;
        "stop"|"down")
            stop_services
            ;;
        "restart")
            stop_services
            build_images
            start_production
            ;;
        "status")
            show_status
            ;;
        "logs")
            shift
            show_logs "$@"
            ;;
        "cli")
            shift
            run_cli "$@"
            ;;
        "test")
            run_tests
            ;;
        "health")
            check_services_health
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
