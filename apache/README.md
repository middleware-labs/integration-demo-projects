# Apache Web Server Setup

## Requirements

- Install [MW Agent v1.6.1](https://app.middleware.io/installation#infrastructures/ubuntu) on your system to monitor the Apache servers.

## Setup Demo Project

- **Required tools**: `docker`, `docker-compose`

- Clone the repository containing the demo project:
  ```bash
  git clone https://github.com/middleware-labs/integration-demo-projects.git
  ```
- Navigate to the `apache` directory
  ```bash
    cd integration-demo-projects/apache
  ```
- Run the following command to start the Apache servers using Docker Compose:
  ```bash
  docker compose up -d
  ```
  This will spin up two Apache servers running on ports `8080` and `8081` by default.
- If you want to run the servers on different ports, provide the desired port numbers as environment variables:

  ```bash
  HTTPD1_PORT="<desired_port_1>" HTTPD2_PORT="<desired_port_2>" docker compose up -d
  ```

  Replace `<desired_port_1>` and `<desired_port_2>` with the port numbers you want to use.

- The setup includes a script that will generate a random number of requests (between 1000 and 10,000) on both Apache servers every minute. This is to simulate traffic for monitoring purposes.

## Monitoring

- Once the servers are up and running, you can use the MW Agent to monitor their performance, resource utilization, and other metrics.
- Refer to the MW Agent documentation for instructions on how to configure and use the monitoring agent.

## Cleanup

- To stop and remove the Apache server containers, run:
  ```bash
  docker compose down
  ```

This will gracefully stop the containers and remove them from your system.
