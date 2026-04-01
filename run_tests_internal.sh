#!/bin/bash
# Start the FastAPI server in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for the server to be ready
echo "Waiting for FastAPI to start..."
timeout 30s bash -c 'until curl -s http://localhost:8000/ > /dev/null; do sleep 1; done'

# Run the full test suite
pytest tests/ -v

# Cleanup
kill $SERVER_PID
