#!/bin/bash

# Setup script for Call2Action project

set -e

echo "🚀 Setting up Call2Action project..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment..."
    uv venv
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source .venv/bin/activate
uv pip install -e .

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OpenAI API key"
fi

# Create output directory
mkdir -p output

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Activate the virtual environment: source .venv/bin/activate"
echo "3. Run the pipeline: python -m call2action.main path/to/your/audio.mp4"
