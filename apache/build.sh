#!/bin/bash

build_image() {
    docker build -t mw-demo-apache .
}

start_container() {
    docker run -d --name mw-demo-apache -p $1:80 mw-demo-apache
    echo "visit http:localhost:8080 in browser"
}

stop_container() {
    docker stop mw-demo-apache
    docker rm mw-demo-apache
}

remove_image() {
    docker rmi mw-demo-apache
}

case "$1" in
    up)
        build_image
         port=${2:-8080}
        start_container $port
        ;;
    down)
        stop_container
        remove_image
        ;;
    *)
        echo "Usage: $0 {up|down}"
        exit 1
        ;;
esac
