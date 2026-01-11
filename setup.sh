#!/bin/bash

# RealDevs Setup Script
# Quick setup for development environment

set -e

echo "🚀 RealDevs Setup Script"
echo "========================"
echo ""

# Check for required tools
check_requirements() {
    echo "Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.14.2 or higher."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found. Please install Node.js 24 LTS or higher."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm not found. Please install npm."
        exit 1
    fi
    
    echo "✅ All requirements met"
}

# Setup backend
setup_backend() {
    echo ""
    echo "Setting up backend..."
    cd apps/api
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ Created Python virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Installed backend dependencies"
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        SECRET_KEY=$(openssl rand -hex 32)
        cat > .env << EOF
FLASK_ENV=development
HIDEVS_SECRET_KEY=$SECRET_KEY
DATABASE_URL=sqlite:///./realdevs.db
FLASK_APP=run.py
PORT=8000
EOF
        echo "✅ Created .env file with random secret key"
    fi
    
    cd ../..
}

# Setup frontend
setup_frontend() {
    echo ""
    echo "Setting up frontend..."
    cd apps/web
    
    # Install dependencies
    npm install > /dev/null 2>&1
    echo "✅ Installed frontend dependencies"
    
    # Create .env.local if it doesn't exist
    if [ ! -f ".env.local" ]; then
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
        echo "✅ Created .env.local file"
    fi
    
    cd ../..
}

# Main setup
main() {
    check_requirements
    setup_backend
    setup_frontend
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To start RealDevs:"
    echo ""
    echo "  Option 1 - Docker (recommended):"
    echo "    docker compose up --build"
    echo ""
    echo "  Option 2 - Manual (two terminals):"
    echo ""
    echo "    Terminal 1 (Backend):"
    echo "      cd apps/api"
    echo "      source venv/bin/activate"
    echo "      python run.py"
    echo ""
    echo "    Terminal 2 (Frontend):"
    echo "      cd apps/web"
    echo "      npm run dev"
    echo ""
    echo "Then open: http://localhost:3000"
    echo ""
    echo "📖 See README.md for more information"
}

main

