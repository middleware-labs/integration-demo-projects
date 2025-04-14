# Redpanda Load Generator 

This project sets up a Redpanda client using Docker and generates load using a Python script packaged in a Docker container.


## 📦 Requirements

- Docker & Docker Compose
- GNU Make (for running commands easily)
---

## 🛠️ Steps
1. Navigate to the project directory:

    ```bash
    cd redpanda
    ```
2. Start containers using `make` command:
    ```bash
    make up
    ```
3. Stop containers using `make` command:
    ```bash
    make down
    ```

---

### Redpanda target for otel config : `127.0.0.1:19644`

### Redpanda dasboard :  <a href="http://127.0.0.1:8090/topics">`http://127.0.0.1:8090/topics`</a>

### Redpanda metrics endpoint for browser : <a href="http://127.0.0.1:19644/metrics">`http://127.0.0.1:19644/metrics`</a>