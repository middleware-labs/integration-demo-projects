# Use OpenJDK 11 as base image
FROM openjdk:11-jre-slim

# Set working directory
WORKDIR /app

# Create user for running the application
RUN useradd -m -s /bin/bash appuser

# Create log directory
RUN mkdir -p /var/log/app && chown -R appuser:appuser /var/log/app

# Copy the built JAR file
COPY target/docker-json-log-reproduction-1.0.0.jar app.jar

# Set environment variables
ENV JAR_NAME=docker-json-log-reproduction-1.0.0.jar
ENV SERVICE_NAME=json-log-reproduction-service
ENV LOG_FORMAT=production

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"] 