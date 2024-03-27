#!/bin/bash

build_image() {
    docker build -t mw-demo-apache .
}

start_container() {
    docker run -d --name mw-demo-apache -p $1:80 mw-demo-apache
    printf "visit http://localhost:%s in browser\n" $1
    printf "visit http://localhost:%s/server-status?refresh=1&auto to see the server stats\n" $1
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
