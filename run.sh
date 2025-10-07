#!/bin/bash

# Helper script for common Call2Action tasks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_help() {
    echo "Call2Action - Video Transcript Pipeline Helper"
    echo ""
    echo "Usage: ./run.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  process <file>    Process a video/audio file"
    echo "  shell             Activate virtual environment shell"
    echo "  test              Run tests"
    echo "  format            Format code with black"
    echo "  lint              Lint code with ruff"
    echo "  install-dev       Install development dependencies"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh process video.mp4"
    echo "  ./run.sh test"
    echo "  ./run.sh shell"
}

activate_venv() {
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}Virtual environment not found. Run ./setup.sh first.${NC}"
        exit 1
    fi
    source .venv/bin/activate
}

case "${1:-help}" in
    process)
        if [ -z "$2" ]; then
            echo "Error: Please provide a file path"
            echo "Usage: ./run.sh process <file>"
            exit 1
        fi
        activate_venv
        echo -e "${GREEN}Processing file: $2${NC}"
        python -m call2action.main "$2"
        ;;
    
    shell)
        activate_venv
        echo -e "${GREEN}Activating virtual environment...${NC}"
        echo "Type 'exit' to leave the environment"
        exec $SHELL
        ;;
    
    test)
        activate_venv
        echo -e "${GREEN}Running tests...${NC}"
        pytest tests/ -v
        ;;
    
    format)
        activate_venv
        echo -e "${GREEN}Formatting code...${NC}"
        black src/ tests/
        ;;
    
    lint)
        activate_venv
        echo -e "${GREEN}Linting code...${NC}"
        ruff check src/ tests/
        ;;
    
    install-dev)
        activate_venv
        echo -e "${GREEN}Installing development dependencies...${NC}"
        uv pip install -e ".[dev]"
        ;;
    
    help|*)
        show_help
        ;;
esac
