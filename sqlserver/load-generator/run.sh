#!/bin/bash

set -e

echo "📦 Starting MSSQL container..."
docker-compose up -d

echo "⏳ Waiting for MSSQL to initialize (10s)..."
sleep 10

echo "🐍 Building Python load generator image..."
docker build -t loadgen-py ./load-generator

echo "🚀 Running the load generator container..."
docker run --network=mssql-load-generator_mssql-network --rm loadgen-py
