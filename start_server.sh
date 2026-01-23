#!/bin/bash

# ============================================
# Start Social Media Backend with Socket.IO
# ============================================

echo "🚀 Starting FastAPI server with Socket.IO support..."
echo ""
echo "⚠️  IMPORTANT: Using socket_app (not app) to enable Socket.IO"
echo ""

# Start the server with socket_app
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000

# Note: 
# - socket_app includes both FastAPI routes AND Socket.IO
# - Using 'app' instead will NOT work with Socket.IO
# - Socket.IO will be available at ws://localhost:8000/socket.io/
