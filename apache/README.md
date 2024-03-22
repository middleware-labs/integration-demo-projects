# Apache Web Server Setup

## Requirements

- Install [MW Agent](https://app.middleware.io/installation#infrastructures/ubuntu)

## Setup Demo Project

-  **Required tools**: `docker`.

- Clone the repository

```bash
git clone https://github.com/middleware-labs/integration-demo-projects.git
```

- Navigate to the `apache-httpd` directory

```bash
cd integration-demo-projects/apache-httpd
```

- Make build script executable

```bash
chmod +x build.sh
```

- Run Script
```bash
./build.sh up
```
- By default it will run on port 8080, If you want to run server on another port, you can provide port as second argument.
 ```bash
./build.sh up 3000
```

- To stop server (It will also remove container and image)
```bash
./build.sh down
```