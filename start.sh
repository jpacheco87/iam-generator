#!/bin/bash

# AWS IAM Generator - Launch Script
# This script starts both the backend FastAPI server and frontend React app

set -e

echo "🚀 Starting AWS IAM Generator..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
    if [ ! -z "$pid" ]; then
        echo "🔪 Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Check if ports are available
echo "🔍 Checking ports..."

if check_port 8000; then
    echo "⚠️  Port 8000 is in use. Stopping existing process..."
    kill_port 8000
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is in use. Stopping existing process..."
    kill_port 3000
fi

# Start backend server
echo "🐍 Starting Python backend server..."
cd "$(dirname "$0")"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install Python dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    pip install fastapi uvicorn python-multipart
    touch .deps_installed
fi

# Start backend in background
echo "🚀 Starting backend server on http://localhost:8000"
python backend_server.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend started successfully
if ! check_port 8000; then
    echo "❌ Backend failed to start!"
    exit 1
fi

echo "✅ Backend started successfully!"

# Start frontend
echo "⚛️  Starting React frontend..."
cd frontend

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing npm dependencies..."
    npm install
fi

# Start frontend in background
echo "🚀 Starting frontend server on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 5

# Check if frontend started successfully
if ! check_port 3000; then
    echo "❌ Frontend failed to start!"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Frontend started successfully!"
echo ""
echo "🎉 AWS IAM Generator is now running!"
echo "   📖 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "👋 Goodbye!"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup INT TERM

# Wait for user to stop
wait
