# Spring Boot REST Example

This demo project is for java application with database integration.
This also contents the Dockerfile, docker-compose.yaml and yaml files to run in the kubernetes environment.

## Requirements

- Database Mysql
- java 17 +

## Description

- Set Environment variables to connect with database.

  | Environment Variable | Description             | Example value                        |
  |----------------------|-------------------------|--------------------------------------|
  | MYSQL_ROOT           | Root username for mysql | root                                 |
  | MYSQL_ROOT_PASSWORD  | Root password           | root                                 |
  | MYSQL_DATABASE       | Database name           | employeedb                           |
  | MYSQL_URL            | Database connection URL | jdbc:mysql://mysqldb:3306/employeedb |

- Update the environment variables and configuration of yaml files of docker and kubernetes.
  - Update the value of MW_API_KEY as per your account
  - Sample values of MW_AGENT_SERVICE for k8s yaml and docker file

    | Environment Variable | Docker     | Kubernetes                               |
    |----------------------|------------|------------------------------------------|
    | MW_AGENT_SERVICE     | 172.17.0.1 | mw-service.mw-agent-ns.svc.cluster.local |

---

## Some basic commands

### Run java application in local environment

**Note:** Set the respective environment variables for the mysql database connection.
Refer the required environment variables in `application.properties` file

- Build java application
  ```bash
  ./mvnw clean package -DskipTests
  ```
- Run java application with middleware javaagent
  ```bash
  MW_API_KEY=your-api-key java -javaagent:middleware-javaagent-1.3.0.jar \ 
    -Dotel.service.name="java-springboot-service" \
    -Dotel.resource.attributes=project.name="java-springboot-project" \ 
    -jar target/springboot-restful-webservices-0.0.1-SNAPSHOT.jar
  ```


### Docker

**Note**: Define environment variables (either in Dockerfile or in command line) if not using the docker compose.
  Refer the environment variables in `docker-compose.yaml` file.

- Build docker image 
  ```bash
  docker build -t java-springboot-demo:latest .
  ```

- Push docker image to docker hub
  ```bash
  docker push java-springboot-demo:latest
  ```

- Run docker image with port forward
  ```bash
  docker run -p 8080:8080 java-springboot-demo:latest
  ```

- Run with docker compose
  - Update the environment variables in docker-compose.yaml
  ```bash
  docker compose up
  ```


### Kubernetes

**Note** : Update the environment variables and image property in respective yaml file.

- Add mysql 
  ```bash
  kubectl apply -f mysql.yaml
  ```

- Run java application
  ```bash
  kubectl apply -f springboot-app.yaml
  ```
