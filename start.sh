#!/bin/bash

# HiLabs AI Document Assistant - Startup Script
echo "🚀 Starting HiLabs AI Document Assistant..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Ollama is installed
print_status "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed!"
    print_status "Installing Ollama..."
    curl -sSL https://ollama.com/install.sh | bash
    if [ $? -eq 0 ]; then
        print_success "Ollama installed successfully!"
    else
        print_error "Failed to install Ollama. Please install manually."
        exit 1
    fi
else
    print_success "Ollama is already installed!"
fi

# Start Ollama service if not running
print_status "Checking Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    print_status "Starting Ollama service..."
    ollama serve &
    sleep 3
    print_success "Ollama service started!"
else
    print_success "Ollama service is already running!"
fi

# Check if llama3.1 model is available
print_status "Checking llama3.1 model..."
if ! ollama list | grep -q "llama3.1"; then
    print_status "Downloading llama3.1 model (this may take a few minutes)..."
    ollama pull llama3.1
    if [ $? -eq 0 ]; then
        print_success "llama3.1 model downloaded successfully!"
    else
        print_error "Failed to download llama3.1 model."
        exit 1
    fi
else
    print_success "llama3.1 model is available!"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created!"
    else
        print_error "Failed to create virtual environment."
        exit 1
    fi
else
    print_success "Virtual environment already exists!"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully!"
else
    print_error "Failed to install dependencies."
    exit 1
fi

# Install pdfplumber if not present
print_status "Ensuring pdfplumber is installed..."
pip install pdfplumber > /dev/null 2>&1

# Test the system
print_status "Testing system components..."
python -c "
from rag import test_system
if test_system():
    print('✅ System test passed!')
else:
    print('❌ System test failed!')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    print_error "System test failed. Please check your setup."
    exit 1
fi

# Kill any existing server processes
print_status "Checking for existing server processes..."
pkill -f "python.*server.py" 2>/dev/null || true

# Start the server
print_status "Starting the HiLabs AI Document Assistant server..."
echo ""
echo "🌟 =============================================== 🌟"
echo "   HiLabs AI Document Assistant is starting!"
echo "   Server will be available at: http://localhost:8000"
echo "🌟 =============================================== 🌟"
echo ""
print_status "Press Ctrl+C to stop the server"
echo ""

# Start the server
python server.py