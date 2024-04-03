# Oracle DB setup with basic authentication using docker compose

## Prerequisites
- Install [MW Agent](https://app.middleware.io/installation#infrastructures/ubuntu) with version `1.6.1` or higher
- Set up Oracle DB Integration.

## Setup Demo Project
- **Required tools**: `docker`, `docker compose`.
- Clone the repository
  ```bash
  git clone https://github.com/middleware-labs/integration-demo-projects.git
  ```
- Navigate to the `oracledb` directory
  ```bash
  cd integration-demo-projects/oracledb
  ```
- Run docker compose file
  ```bash
  docker compose up -d
  
- Default username and service name for **oracle:express** image
  - Username: `system`
  - service: `XE`
  - Credentials can be changed from file `oracledb/config.json`. for respective oracle db services

## Database Viewer Tools

- Use Database Viewer Tools like **DataGrip** or **DBeaver** etc which supports Oracle DB.
- Connect data source using required credentials of Oracle DB services on one of this tool to view generated data.