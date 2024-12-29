#!/bin/bash
set -e

echo "Checking system resources..."

DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt 70 ]; then
    echo "Cleaning up docker system..."
    echo "Current disk usage: ${DISK_USAGE}%"
    docker system prune -af --volumes
else
    echo "Cleanup not needed"
    echo "Current disk usage: ${DISK_USAGE}%"
fi
