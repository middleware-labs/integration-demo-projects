terraform {
  required_providers {
    null = {
      source = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

provider "null" {}

resource "null_resource" "apache" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/apache/docker-compose.yaml up -d"
  }
}

resource "null_resource" "cassandra" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/cassandra/docker-compose.yaml up -d"
  }
}

resource "null_resource" "elasticsearch" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/elasticsearch/docker-compose.yaml up -d"
  }
}

resource "null_resource" "kafka" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/kafka/kafka_auth_sasl_plaintext/docker-compose.yaml up -d"
  }
}

resource "null_resource" "mongodb" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/mongodb/docker-compose.yaml up -d"
  }
}

resource "null_resource" "mysql" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/mysql/docker-compose.yaml up -d"
  }
}

resource "null_resource" "oracledb" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/oracledb/docker-compose.yaml up -d"
  }
}

resource "null_resource" "postgres" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/postgres/docker-compose.yaml up -d"
  }
}

resource "null_resource" "redis" {
  provisioner "local-exec" {
    command = "docker compose --file=/root/integration-demo-projects/redis/docker-compose.yaml up -d"
  }
}
