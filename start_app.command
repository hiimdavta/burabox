#!/bin/bash

# Get the directory where the .command file is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if something is running on port 5051 and kill it
PID=$(lsof -ti:5051)
if [ ! -z "$PID" ]; then
    echo "Stopping existing Flask application (PID: $PID)..."
    kill $PID
    # Wait for the process to fully stop
    while kill -0 $PID 2>/dev/null; do
        sleep 1
    done
    echo "Existing Flask application stopped."
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3 from https://www.python.org/downloads/macos/"
    exit 1
fi

# Check if required packages are installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Error: Flask is not installed!"
    echo "Please run: pip3 install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Start Flask app in the background
echo "Starting Flask application..."
python3 app.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Get the machine's IP address
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)

# Print available URLs
echo
echo "Server is running and available at:"
echo "- Local: http://localhost:5051"
if [ ! -z "$IP" ]; then
    echo "- Network: http://$IP:5051"
fi
echo

# Open the browser
open http://localhost:5051

# Keep the terminal window open
wait $FLASK_PID 