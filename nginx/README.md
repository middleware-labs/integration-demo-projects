# Nginx Load Balancing Demo with VTS Module

This project demonstrates load balancing between two FastAPI services using Nginx with the Virtual Host Traffic Status (VTS) module for monitoring.
Prerequisites

- Docker
- docker-compose
- curl (for testing)

## Quick Start

Create necessary configuration files as shown in the project structure.

Build and start the services:

```
docker-compose up --build
```

## Accessing Services

Test the basic endpoint:
``` bash
curl http://localhost:8000/
```

Create a new item:
``` bash
curl -X POST http://localhost:8000/item \
  -H "Content-Type: application/json" \
  -d '{"name": "test item", "price": 10.99, "desc": "A test item"}'
```

Get all items:
```
curl http://localhost:8000/items
```

## Monitoring

### VTS Module Features

- Access detailed traffic statistics at `/status`
- Monitor request counts, bandwidth usage, and response times
- View per-server metrics for load balancing

### Basic Nginx Status

- Access basic Nginx metrics at `/nginx_status`
- View current connections and request statistics

### Load Balancer Configuration
The Nginx load balancer is configured with:

- Round-robin distribution between two FastAPI servers
- HTTP headers for tracking (X-Real-IP, X-Forwarded-For)
- Server identification header (X-Served-By)
- Access restrictions for status pages



