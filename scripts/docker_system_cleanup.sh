#!/bin/bash

echo "Running docker cleanup at $(date)" >> /var/log/docker_cleanup.log

docker system prune -af >> /var/log/docker_cleanup.log 2>&1
docker volume prune -f >> /var/log/docker_cleanup.log 2>&1
docker network prune -f >> /var/log/docker_cleanup.log 2>&1

echo "Cleanup completed." >> /var/log/docker_cleanup.log
