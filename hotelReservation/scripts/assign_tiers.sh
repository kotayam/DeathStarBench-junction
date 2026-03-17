#!/bin/bash

DOCKER="sudo docker"

# 1. Fetch all node hostnames from Docker Swarm into an array
# We sort them to ensure consistent ordering (e.g., node-1, node-2, node-3, node-4)
mapfile -t NODES < <($DOCKER node ls --format "{{.Hostname}}" | sort)

# 2. Define the exact tiers we want to assign
TIERS=("gateway" "compute" "cache" "data")

echo "Found ${#NODES[@]} nodes in the Swarm cluster."

# 3. Loop through the nodes and assign the corresponding tier
for i in "${!NODES[@]}"; do
    NODE="${NODES[$i]}"
    TIER="${TIERS[$i]}"

    # Fallback just in case you add more than 4 nodes later
    if [ -z "$TIER" ]; then
        TIER="compute" 
    fi

    echo "Assigning label 'tier=$TIER' to node: $NODE"
    $DOCKER node update --label-add tier=$TIER "$NODE" > /dev/null
done

echo "----------------------------------------"
echo "Label assignment complete! Verifying:"

# 4. Print out the nodes and their new labels to confirm
$DOCKER node ls -q | xargs $DOCKER node inspect -f '{{ .Description.Hostname }}: {{ .Spec.Labels }}'
