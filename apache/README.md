
# Apache Web Server Setup

## Requirements

- Install [MW Agent v1.6.1](https://app.middleware.io/installation#infrastructures/ubuntu)

## Setup Demo Project

-  **Required tools**: `docker`, `curl` and a `linux` machine.

- Clone the repository

```bash
git  clone  https://github.com/middleware-labs/integration-demo-projects.git
```

- Navigate to the `apache` directory

```bash
cd  integration-demo-projects/apache
```

- Make build script executable
```bash
chmod  +x  build.sh
```

- Make load script executable
```bash
chmod  +x  load.sh
```

- Run Script

```bash
./build.sh up
```

- By default it will run on port 8080 and 8081, If you want to run server on another port, you can provide port as second argument.
```bash
./build.sh up [port]
```
- It will create two apache servers, where 1st will run on provided port and other on port + 1.

- To stop server
```bash
./build.sh down
```

- You can also make a lot of requests concurrently to generate data using `load.sh`
```bash
Usage: ./load.sh <concurrency> <total_requests> <server_url1> [<server_url2> ...]
```