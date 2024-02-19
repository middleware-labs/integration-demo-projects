# Kafka Setup with Basic SASL Plaintext authentication

## Requirements

- Install [MW Agent](https://app.middleware.io/installation#infrastructures/ubuntu)
- Download latest jar file from [opentelemetry-jmx-metrics.jar](https://github.com/open-telemetry/opentelemetry-java-contrib/releases)
- Set up the kafka integration.

## Setup Demo Project

- **Required tools**: `docker`, `docker compose`.
- Clone the repository
  ```bash
  git clone https://github.com/middleware-labs/integration-demo-projects.git
  ```
- Navigate to the `kafka_auth_sasl_plaintext` directory
  ```bash
  cd integration-demo-projects/kafka/kafka_auth_sasl_plaintext
  ```
- Run docker compose file
  ```bash
  docker compose up -d
  ```
- Run Producer and Consumer to generate data.
  - To run Consumer
    ```bash
    python3 consumer.py
    ```
  - To run Producer
    ```bash
    python3 producer.py
    ```

- Default username and password 
  - Username: `mwkafkausername`
  - Password: `mwkafkapassword`
  - Credentials can be changed from file `kafka/kafka_auth_sasl_plaintext/configs/kafka_server_jaas.conf`.
