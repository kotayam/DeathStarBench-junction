#!/bin/bash

set -e

DOCKER="sudo docker"
STACK_NAME="hotel"
COMPOSE_FILE="docker-compose.yml"

echo "======================================================"
echo "1. Building custom images on all Swarm nodes..."
echo "======================================================"

# Fetch all node hostnames from the Swarm manager
mapfile -t NODES < <($DOCKER node ls --format "{{.Hostname}}")

CURRENT_NODE=$(hostname)

# for NODE in "${NODES[@]}"; do
#     # Skip the node running the script
#     if [ "$NODE" == "$CURRENT_NODE" ]; then
#         echo "--> Skipping local manager node ($NODE)..."
#         continue
#     fi
#
#     echo "--> Compiling 'review' and 'attractions' on $NODE..."
#
#     # If this SSH command fails, print a warning and exit the entire script
#     ssh -o StrictHostKeyChecking=no "$USER@$NODE" "cd $PWD && docker-compose build review attractions" || {
#         echo "❌ ERROR: Build failed on $NODE. Aborting deployment."
#         exit 1
#     }
# done

echo ""
echo "======================================================"
echo "2. Tearing down the old stack..."
echo "======================================================"
set +e
$DOCKER stack rm $STACK_NAME
set -e

# Swarm needs time to release the overlay network IPs and kill the containers
echo "Waiting 15 seconds for networks and containers to fully terminate..."
sleep 15

echo ""
echo "======================================================"
echo "3. Deploying the strict-topology stack..."
echo "======================================================"
$DOCKER stack deploy -c $COMPOSE_FILE $STACK_NAME

echo ""
echo "======================================================"
echo "Deployment triggered! Your cluster is booting."
echo "Run 'docker service ls' to watch the replicas hit 1/1."
echo "======================================================"
