#!/bin/bash

URL="${1:-http://164.90.240.114/work-cpu-bound}"
INTERVAL="${2:-1}"
i=1

echo "Monitoring $URL every $INTERVAL seconds..."
echo "Request No / Machine"

while true; do
    MACHINE=$(curl -s "$URL" | jq -r '.machine')
    echo "$i / $MACHINE"
    i=$((i+1))
    sleep "$INTERVAL"
done

