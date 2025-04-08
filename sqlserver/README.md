# MSSQL Load Generator

This project sets up a SQL Server using Docker and generates database load using a Python script packaged in a Docker container.

---

## 📦 Requirements

- Docker & Docker Compose
- GNU Make (for running commands easily)
- (Optional) Python 3.8+ and ODBC driver if you want to run the script outside Docker

---

## 🚀 Project Setup

### ✅ Clone the project

```bash
git clone https://github.com/middleware-labs/integration-demo-projects.git
cd sqlserver
make all  # 🚀 This starts MSSQL, builds the load generator, and inserts sample data
```
