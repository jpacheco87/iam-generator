#!/bin/bash
set -e

# AWS IAM Generator - Docker Entrypoint Script
# Handles initialization and different run modes

echo "🐳 Starting AWS IAM Generator Container..."

# Function to wait for dependencies
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "⏳ Waiting for $service_name at $host:$port..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "✅ $service_name is ready!"
}

# Function to run database migrations or setup
setup_application() {
    echo "🔧 Setting up application..."
    
    # Create necessary directories
    mkdir -p /app/logs /app/data
    
    # Initialize any required data
    python -c "
from iam_generator.permissions_db import IAMPermissionsDatabase
print('📊 Initializing permissions database...')
db = IAMPermissionsDatabase()
print('✅ Database initialized successfully!')
"
    
    echo "✅ Application setup complete!"
}

# Function to run the backend server
run_backend() {
    echo "🚀 Starting FastAPI backend server..."
    setup_application
    exec uvicorn backend_server:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
}

# Function to run the CLI
run_cli() {
    echo "🖥️  Starting CLI mode..."
    setup_application
    
    # If arguments provided, run them
    if [ $# -gt 1 ]; then
        shift # Remove 'cli' argument
        exec python -m iam_generator.main "$@"
    else
        # Interactive mode
        exec python -m iam_generator.main --help
    fi
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    setup_application
    exec python -m pytest tests/ -v --tb=short
}

# Function to run development mode
run_dev() {
    echo "🔧 Starting development mode..."
    setup_application
    
    # Install development dependencies
    pip install pytest pytest-cov black flake8 mypy
    
    # Run backend with auto-reload
    exec uvicorn backend_server:app --host 0.0.0.0 --port ${PORT:-8000} --reload --log-level debug
}

# Main execution logic
case "${1:-backend}" in
    "backend")
        run_backend
        ;;
    "cli")
        shift
        run_cli "$@"
        ;;
    "test")
        run_tests
        ;;
    "dev")
        run_dev
        ;;
    "bash")
        exec /bin/bash
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Available commands:"
        echo "  backend  - Start FastAPI backend server (default)"
        echo "  cli      - Run CLI with optional arguments"
        echo "  test     - Run test suite"
        echo "  dev      - Start development mode with auto-reload"
        echo "  bash     - Start interactive bash shell"
        exit 1
        ;;
esac
