#!/bin/bash

start_container() {
    validate_int "$1"

    p1="$1"
    p2=$((p1 + 1))

    HTTPD1_PORT="$p1" HTTPD2_PORT="$p2" docker-compose up -d
}

validate_int() {
    if ! [[ "$1" =~ ^[0-9]+$ ]]; then
        echo "Error: '$1' is not a valid integer."
        exit 1
    fi
}

stop_container() {
    docker-compose down
}

case "$1" in
    up)
        port="${2:-8080}"
        start_container "$port"
        ;;
    down)
        stop_container
        ;;
    *)
        echo "Usage: $0 {up|down} [port]"
        echo "Note: It will create two servers on port and port + 1, default port = 8080"
        exit 1
        ;;
esac
