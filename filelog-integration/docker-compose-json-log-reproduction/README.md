# Docker JSON Log Format Reproduction

This project reproduces the exact log format you described where:
- **Top-level JSON keys** are pure JSON (`log`, `stream`, `time`)
- **Nested JSON** (within the `log` field) is stringified

## Log Format Example

The application will generate logs in this format:

```json
{
  "log": "{\"instant\":{\"epochSecond\":1738234567,\"nanoOfSecond\":123000000},\"thread\":\"http-nio-8080-exec-1\",\"level\":\"WARN\",\"loggerName\":\"com.example.controller.LogGeneratorController\",\"message\":\"token blocked SpApiClient.CacheTokenKey(amazonChannel=AMAZON_US, actionType=getCatalogItem, sellerId=A123456Z89Y), count 10\",\"endOfBatch\":false,\"loggerFqcn\":\"org.apache.logging.log4j.spi.AbstractLogger\",\"contextMap\":{},\"threadId\":25,\"threadPriority\":5,\"jarName\":\"docker-json-log-reproduction-1.0.0.jar\",\"serviceName\":\"json-log-reproduction-service\"}\r\n",
  "stream": "stdout",
  "time": "2025-01-30T12:06:27.627205893Z"
}
```

## How It Works

1. **Java Application**: Outputs structured JSON logs using Log4j2 JsonLayout to stdout
2. **Docker json-file Driver**: Captures stdout and wraps it in Docker's log format
3. **Result**: The application's JSON becomes a stringified value in Docker's `log` field

## Quick Start

### 1. Build and Run

```bash
# Build the application
mvn clean package

# Start with Docker Compose
docker-compose up --build

# Or run just the application
docker-compose up --build json-log-app
```

### 2. Generate Logs

The application provides several endpoints to generate different types of logs:

```bash
# Basic health check (generates startup logs)
curl http://localhost:8080/

# Generate multiple log entries
curl "http://localhost:8080/generate-logs?count=5"

# Simulate the exact API scenario from your example
curl http://localhost:8080/api-simulation

# Generate error logs with stack traces
curl http://localhost:8080/error-simulation
```

### 3. View Logs

```bash
# View container logs (shows the Docker JSON format)
docker logs json-log-reproduction-container

# Follow logs in real-time
docker logs json-log-reproduction-container --follow

# View raw Docker log files (requires root/sudo)
sudo cat /var/lib/docker/containers/$(docker inspect -f '{{.Id}}' json-log-reproduction-container)/json-log-reproduction-container-json.log
```

## Log Configuration

The `log4j2.xml` configuration is based on your client's setup:

- **JsonLayout**: Outputs structured JSON with custom fields
- **Console Output**: Logs go to stdout (captured by Docker)
- **Environment Variables**: 
  - `JAR_NAME`: Sets the jar name in logs
  - `SERVICE_NAME`: Sets the service name in logs
  - `LOG_FORMAT`: Controls log format (dev vs production)

## Docker Configuration

The `docker-compose.yml` uses:

```yaml
logging:
  driver: json-file  # This creates the nested JSON format
  options:
    max-size: "100m"
    max-file: "5"
```

## Understanding the Format

### Application Log (what the Java app outputs):
```json
{"instant":{"epochSecond":1738234567,"nanoOfSecond":123000000},"thread":"http-nio-8080-exec-1","level":"WARN","loggerName":"com.example.controller.LogGeneratorController","message":"token blocked SpApiClient.CacheTokenKey(amazonChannel=AMAZON_US, actionType=getCatalogItem, sellerId=A123456Z89Y), count 10","endOfBatch":false,"loggerFqcn":"org.apache.logging.log4j.spi.AbstractLogger","contextMap":{},"threadId":25,"threadPriority":5,"jarName":"docker-json-log-reproduction-1.0.0.jar","serviceName":"json-log-reproduction-service"}
```

### Docker-Wrapped Log (what your filelogreceiver sees):
```json
{
  "log": "{\"instant\":{\"epochSecond\":1738234567,\"nanoOfSecond\":123000000},\"thread\":\"http-nio-8080-exec-1\",\"level\":\"WARN\",\"loggerName\":\"com.example.controller.LogGeneratorController\",\"message\":\"token blocked SpApiClient.CacheTokenKey(amazonChannel=AMAZON_US, actionType=getCatalogItem, sellerId=A123456Z89Y), count 10\",\"endOfBatch\":false,\"loggerFqcn\":\"org.apache.logging.log4j.spi.AbstractLogger\",\"contextMap\":{},\"threadId\":25,\"threadPriority\":5,\"jarName\":\"docker-json-log-reproduction-1.0.0.jar\",\"serviceName\":\"json-log-reproduction-service\"}\r\n",
  "stream": "stdout", 
  "time": "2025-01-30T12:06:27.627205893Z"
}
```

## File Structure

```
docker-compose-json-log-reproduction/
├── src/main/java/com/example/
│   ├── JsonLogReproductionApplication.java
│   └── controller/LogGeneratorController.java
├── src/main/resources/log4j2.xml
├── pom.xml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Testing Your Agent

Once running, you can test your filelogreceiver against:

- **Docker log directory**: `/var/lib/docker/containers/*/json-log-reproduction-container-json.log`
- **Log format**: Matches exactly what your client produces
- **Content**: Similar API call patterns and log structures

## Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes and images
docker-compose down -v --rmi all
```

This reproduction should give you the exact same log format your client is generating! 