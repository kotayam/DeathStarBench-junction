#!/bin/bash

DOCKER="sudo docker"
STACK_NAME="hotel"

echo "======================================================"
echo " Verifying Strict 4-Tier Topology for Stack: $STACK_NAME"
echo "======================================================"

# Fetch all node IDs in the swarm
mapfile -t NODE_IDS < <($DOCKER node ls -q)

for NODE_ID in "${NODE_IDS[@]}"; do
    # Extract the hostname and the custom 'tier' label
    HOSTNAME=$($DOCKER node inspect --format '{{ .Description.Hostname }}' "$NODE_ID")
    TIER=$($DOCKER node inspect --format '{{ index .Spec.Labels "tier" }}' "$NODE_ID")

    # Fallback just in case a node is missing a label
    if [ -z "$TIER" ]; then
        TIER="UNASSIGNED"
    fi

    echo ""
    echo "🟢 NODE: $HOSTNAME | TIER: [$TIER]"
    echo "------------------------------------------------------"

    # Fetch containers running on this specific node for this stack
    # We strip the header with 'tail -n +2' and add indentation for readability
    SERVICES=$($DOCKER stack ps "$STACK_NAME" --filter "node=$HOSTNAME" --format "{{.Name}}  -->  {{.CurrentState}}")

    if [ -z "$SERVICES" ]; then
        echo "   (No active services running on this node)"
    else
        echo "$SERVICES" | sed 's/^/   - /'
    fi
done

echo ""
echo "======================================================"
echo "✅ Topology check complete. Cross-reference with your design."
echo "======================================================"
