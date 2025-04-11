# 🐘 Postgres Load Generator

This project sets up a PostgreSQL database using Docker and generates database load using a Python script packaged in a Docker container.

---

## 📦 Requirements

- Docker & Docker Compose
- GNU Make (for running commands easily)
- (Optional) Python 3.8+ and psycopg2 if you want to run the script outside Docker

---

## 🚀 Project Setup

### ✅ Clone the project

```bash
git clone https://github.com/middleware-labs/integration-demo-projects.git
cd postgres
make all  # 🚀 This starts Postgres, builds the load generator, and inserts sample data
```

### ⚠️ Important Note

If you're using a Linux machine where PostgreSQL is already running on port `5432` (e.g., via your Bifrost Docker setup with credentials stored in `.secrets.local`), this demo may conflict with the existing instance.

#### To avoid port conflicts, it's recommended to run this demo project on a Windows machine only.
