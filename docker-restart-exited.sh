#!/bin/bash

# Function to restart exited containers
restart_exited_containers() {
    exited_containers=$(docker ps -a -f "status=exited" -q)
    if [ ! -z "$exited_containers" ]; then
        echo "Restarting exited containers..."
        for container in $exited_containers; do
            docker restart $container
            echo "Restarted container $container"
        done
    else
        echo "No exited containers to restart."
    fi
}

# Continuous monitoring loop
while true
do
    restart_exited_containers
    sleep 60  # Adjust the sleep interval as needed
done
