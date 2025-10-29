#!/bin/bash

# Azure Live Interpreter Agent Deployment Script
# This script helps deploy the agent to LiveKit Cloud or local Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_info "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    print_info "✓ Docker found"
}

check_env_vars() {
    print_info "Checking environment variables..."

    if [ -z "$AZURE_SPEECH_KEY" ]; then
        print_error "AZURE_SPEECH_KEY is not set"
        echo "Please set: export AZURE_SPEECH_KEY='your-key'"
        exit 1
    fi

    if [ -z "$AZURE_SPEECH_REGION" ]; then
        print_error "AZURE_SPEECH_REGION is not set"
        echo "Please set: export AZURE_SPEECH_REGION='eastus'"
        exit 1
    fi

    print_info "✓ Azure credentials configured"
}

build_docker() {
    print_info "Building Docker image..."

    docker build -t azure-live-interpreter:latest .

    if [ $? -eq 0 ]; then
        print_info "✓ Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

test_local() {
    print_info "Testing agent locally..."

    # Check for LiveKit dev credentials
    LIVEKIT_URL="${LIVEKIT_URL:-ws://localhost:7880}"
    LIVEKIT_API_KEY="${LIVEKIT_API_KEY:-devkey}"
    LIVEKIT_API_SECRET="${LIVEKIT_API_SECRET:-secret}"

    print_info "Starting agent with:"
    print_info "  LiveKit URL: $LIVEKIT_URL"
    print_info "  Azure Region: $AZURE_SPEECH_REGION"

    docker run -it --rm \
        -e AZURE_SPEECH_KEY="$AZURE_SPEECH_KEY" \
        -e AZURE_SPEECH_REGION="$AZURE_SPEECH_REGION" \
        -e AZURE_SPEAKER_PROFILE_ID="${AZURE_SPEAKER_PROFILE_ID:-}" \
        -e LIVEKIT_URL="$LIVEKIT_URL" \
        -e LIVEKIT_API_KEY="$LIVEKIT_API_KEY" \
        -e LIVEKIT_API_SECRET="$LIVEKIT_API_SECRET" \
        -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
        azure-live-interpreter:latest
}

push_to_registry() {
    print_info "Pushing to Docker registry..."

    if [ -z "$DOCKER_REGISTRY" ]; then
        print_error "DOCKER_REGISTRY is not set"
        echo "Please set: export DOCKER_REGISTRY='your-registry.io/your-username'"
        exit 1
    fi

    FULL_IMAGE="$DOCKER_REGISTRY/azure-live-interpreter:latest"

    print_info "Tagging image: $FULL_IMAGE"
    docker tag azure-live-interpreter:latest "$FULL_IMAGE"

    print_info "Pushing to registry..."
    docker push "$FULL_IMAGE"

    if [ $? -eq 0 ]; then
        print_info "✓ Image pushed successfully: $FULL_IMAGE"
    else
        print_error "Failed to push image"
        exit 1
    fi
}

deploy_to_cloud() {
    print_info "Deploying to LiveKit Cloud..."

    if [ -z "$LIVEKIT_CLOUD_URL" ]; then
        print_error "LIVEKIT_CLOUD_URL is not set"
        echo "Please set: export LIVEKIT_CLOUD_URL='wss://your-project.livekit.cloud'"
        exit 1
    fi

    if [ -z "$LIVEKIT_CLOUD_API_KEY" ]; then
        print_error "LIVEKIT_CLOUD_API_KEY is not set"
        exit 1
    fi

    if [ -z "$LIVEKIT_CLOUD_API_SECRET" ]; then
        print_error "LIVEKIT_CLOUD_API_SECRET is not set"
        exit 1
    fi

    # Check if livekit-cli is installed
    if ! command -v livekit-cli &> /dev/null; then
        print_warn "livekit-cli is not installed"
        print_info "Please deploy manually via LiveKit Cloud Dashboard"
        print_info "Or install CLI: brew install livekit-cli"
        exit 1
    fi

    print_info "Deploying agent..."
    # Deployment command here (depends on LiveKit CLI syntax)
    print_info "✓ Deploy via LiveKit Cloud Dashboard with these credentials"
}

show_usage() {
    cat << EOF
Azure Live Interpreter Agent Deployment Script

Usage:
  ./deploy.sh [command]

Commands:
  build       Build Docker image
  test        Test agent locally
  push        Push image to Docker registry
  deploy      Deploy to LiveKit Cloud
  all         Build, test, push, and deploy

Environment Variables Required:
  AZURE_SPEECH_KEY           Azure Speech Service subscription key
  AZURE_SPEECH_REGION        Azure region (e.g., eastus)

Optional:
  AZURE_SPEAKER_PROFILE_ID   Custom speaker profile ID
  DOCKER_REGISTRY            Docker registry URL (for push)
  LIVEKIT_CLOUD_URL          LiveKit Cloud WebSocket URL
  LIVEKIT_CLOUD_API_KEY      LiveKit Cloud API key
  LIVEKIT_CLOUD_API_SECRET   LiveKit Cloud API secret
  LOG_LEVEL                  Logging level (default: INFO)

Examples:
  # Build and test locally
  export AZURE_SPEECH_KEY="your-key"
  export AZURE_SPEECH_REGION="eastus"
  ./deploy.sh build
  ./deploy.sh test

  # Push to registry
  export DOCKER_REGISTRY="docker.io/username"
  ./deploy.sh push

  # Full deployment
  ./deploy.sh all

For detailed deployment guide, see DEPLOYMENT.md
EOF
}

# Main script
main() {
    case "${1:-help}" in
        build)
            check_dependencies
            build_docker
            ;;
        test)
            check_dependencies
            check_env_vars
            test_local
            ;;
        push)
            check_dependencies
            push_to_registry
            ;;
        deploy)
            deploy_to_cloud
            ;;
        all)
            check_dependencies
            check_env_vars
            build_docker
            print_info "Local test skipped in 'all' mode. Run './deploy.sh test' to test."
            push_to_registry
            deploy_to_cloud
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
