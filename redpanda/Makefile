.PHONY: all up build run logs down clean

# Start only the MSSQL service
up:
	docker compose up -d

# Build the Python load generator Docker image
build:
	docker build -t redpanda-loadgen .


# Run the load generator container and connect it to the Redpanda container network
run:
	docker run --network=redpanda-quickstart-one-broker_redpanda_network redpanda-loadgen

# Show live container logs
logs:
	docker compose logs -f

# Stop and remove containers + volumes
down:
	docker compose down -v 

# Clean all and rerun the whole process
all: up build run
