#!/bin/bash

set -e

echo "🚀 Docker JSON Log Format Reproduction Test"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}🔷 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker compose >/dev/null 2>&1; then
    print_error "docker compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

print_step "Building the application with Maven..."
mvn clean package -q

print_success "Application built successfully"

print_step "Starting Docker Compose services..."
docker compose up -d --build

print_success "Services started"

# Wait for application to be ready
print_step "Waiting for application to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/ >/dev/null 2>&1; then
        print_success "Application is ready!"
        break
    fi
    echo -n "."
    sleep 2
done

if ! curl -s http://localhost:8080/ >/dev/null 2>&1; then
    print_error "Application failed to start"
    docker compose logs
    exit 1
fi

echo
print_step "Generating test logs..."

# Generate various types of logs
curl -s http://localhost:8080/ > /dev/null
print_success "Health check logs generated"

curl -s "http://localhost:8080/generate-logs?count=3" > /dev/null
print_success "Random logs generated"

curl -s http://localhost:8080/api-simulation > /dev/null
print_success "API simulation logs generated"

curl -s http://localhost:8080/error-simulation > /dev/null
print_success "Error simulation logs generated"

echo
print_step "Showing Docker JSON log format..."
echo
print_warning "Example of the nested JSON format your filelogreceiver will see:"
echo

# Get container ID
CONTAINER_ID=$(docker inspect -f '{{.Id}}' json-log-reproduction-container)

# Show some recent logs in JSON format
echo -e "${YELLOW}--- Docker JSON Log Sample ---${NC}"
sudo cat "/var/lib/docker/containers/${CONTAINER_ID}/${CONTAINER_ID}-json.log" | tail -3 | jq . 2>/dev/null || {
    echo "Raw log format (install jq for pretty printing):"
    sudo cat "/var/lib/docker/containers/${CONTAINER_ID}/${CONTAINER_ID}-json.log" | tail -3
}

echo
echo -e "${YELLOW}--- Explanation ---${NC}"
echo "1. The 'log' field contains the stringified JSON from your Java app"
echo "2. The 'stream' field indicates stdout/stderr"  
echo "3. The 'time' field is Docker's timestamp"
echo "4. This is exactly what your filelogreceiver sees in /var/lib/docker"

echo
print_step "Log file location:"
echo "/var/lib/docker/containers/${CONTAINER_ID}/${CONTAINER_ID}-json.log"

echo
print_step "To view live logs:"
echo "docker logs json-log-reproduction-container --follow"

echo
print_step "To generate more logs:"
echo "curl http://localhost:8080/api-simulation"
echo "curl \"http://localhost:8080/generate-logs?count=10\""

echo
print_success "Test completed! The reproduction environment is running."
print_warning "Use 'docker compose down' to stop the services." 