#!/usr/bin/env bash

# Install Harness Docker Delegate
docker run -d --cpus=1 --memory=2g \
  -e DELEGATE_NAME=demo-rtech \
  -e NEXT_GEN="true" \
  -e DELEGATE_TYPE="DOCKER" \
  -e ACCOUNT_ID=x2LhkpHpTAmYbuz5kvPkiQ \
  -e DELEGATE_TOKEN=NWE5NmMzMWUwYmUwZTVmY2E3ZDI4Yjc3OTVjNzQ5ZTE= \
  -e DELEGATE_TAGS="" \
  -e MANAGER_HOST_AND_PORT=https://app.harness.io \
  us-docker.pkg.dev/gar-prod-setup/harness-public/harness/delegate:26.08.89804

# Enable auto-upgrade for Docker Delegate
docker run -d --cpus=0.1 --memory=100m \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e ACCOUNT_ID=x2LhkpHpTAmYbuz5kvPkiQ \
  -e MANAGER_HOST_AND_PORT=https://app.harness.io \
  -e UPGRADER_WORKLOAD_NAME=demo-rtech \
  -e UPGRADER_TOKEN=NWE5NmMzMWUwYmUwZTVmY2E3ZDI4Yjc3OTVjNzQ5ZTE= \
  -e CONTAINER_STOP_TIMEOUT=3600 \
  -e SCHEDULE="0 */1 * * *" \
  harness/upgrader:latest
