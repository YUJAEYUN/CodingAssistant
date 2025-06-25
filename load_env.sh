#!/bin/bash
# Script to load environment variables from .env file

# Check if .env file exists
if [ -f .env ]; then
    echo "🔑 Loading environment variables from .env file..."
    
    # Export variables from .env file
    export $(grep -v '^#' .env | xargs)
    
    echo "✅ Environment variables loaded successfully!"
    echo "📋 Available API keys:"
    
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "   - OpenAI API Key: ****${OPENAI_API_KEY: -4}"
    else
        echo "   - OpenAI API Key: ❌ Not set"
    fi
    
    if [ ! -z "$ANTHROPIC_API_KEY" ]; then
        echo "   - Anthropic API Key: ****${ANTHROPIC_API_KEY: -4}"
    else
        echo "   - Anthropic API Key: ❌ Not set"
    fi
    
else
    echo "❌ .env file not found!"
    echo "Please create a .env file with your API keys."
    exit 1
fi
