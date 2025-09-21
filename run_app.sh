#!/bin/bash

# Task Management System Startup Script

echo "🚀 Starting Task Management System..."
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if MySQL container is running
if ! docker ps | grep -q "task_management_mysql"; then
    echo "🐳 Starting MySQL container..."
    docker start task_management_mysql || {
        echo "❌ Failed to start MySQL container. Creating new one..."
        docker run -d --name task_management_mysql \
            -e MYSQL_ROOT_PASSWORD=password \
            -e MYSQL_DATABASE=task_management \
            -e MYSQL_USER=app_user \
            -e MYSQL_PASSWORD=app_password \
            -p 3307:3306 \
            -v ./init.sql:/docker-entrypoint-initdb.d/init.sql \
            mysql:8.0
    }

    echo "⏳ Waiting for MySQL to start..."
    sleep 10
fi

echo "✅ MySQL container is running"

# Start FastAPI backend
echo "🚀 Starting FastAPI backend on port 8001..."
uvicorn main:app --port 8001 --reload &
FASTAPI_PID=$!

# Wait for FastAPI to start
sleep 3

# Start Streamlit frontend
echo "🎨 Starting Streamlit frontend on port 8502..."
streamlit run streamlit_app.py --server.port 8502 &
STREAMLIT_PID=$!

echo ""
echo "🎉 Task Management System is now running!"
echo "========================================"
echo "📊 Dashboard (Streamlit): http://localhost:8502"
echo "🔧 API Documentation: http://localhost:8001/docs"
echo "🔌 API Endpoint: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to handle cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $FASTAPI_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait