#!/bin/bash

if [[ -z "$1" ]]; then
    echo
    echo "    usage: check_http.sh '<url to your website>'"
    echo
    exit
fi

url1="$1"
url1_error=0

while :; do
    date_str=$(date +%Y-%m-%d:%H:%M:%S)
    curl -v --insecure --max-time 5 "$url1" 2> /dev/null > /dev/null
    if [[ $? -eq 0 ]]; then
        if [[ $url1_error -eq 1 ]]; then
            url1_error=0
            echo "$date_str no error"
        fi
    else
        if [[ $url1_error -eq 0 ]]; then
            url1_error=1
            echo "$date_str $url1"
        fi
        beep -f 50 -l 50 -r 4
    fi

    sleep 10 
done
