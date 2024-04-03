#!/bin/bash

validate_int() {
    if ! [[ "$1" =~ ^[0-9]+$ ]]; then
        echo "Error: '$1' is not a valid integer."
        exit 1
    fi
}

CONCURRENCY=${1}
TOTAL_REQUESTS=${2}

if [ -z "$CONCURRENCY" ] || [ -z "$TOTAL_REQUESTS" ] || [ "$#" -lt 3 ]; then
    echo "Usage: $0 <concurrency> <total_requests> <server_url1> [<server_url2> ...]"
    exit 1
fi

validate_int "$CONCURRENCY"
validate_int "$TOTAL_REQUESTS"

shift 2

make_request() {
    for url in "$@"; do
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
        echo "URL: $url | Status Code: $status_code"
    done
}

export -f make_request

seq "$TOTAL_REQUESTS" | xargs -P "$CONCURRENCY" -I {} bash -c 'make_request "$@"' _ "$@"
