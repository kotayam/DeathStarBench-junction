#!/bin/bash

# 1. Validate input
if [ -z "$1" ]; then
    echo "Usage: sudo $0 <container_name_or_substring>"
    echo "Example: sudo $0 hotel_reservation"
    exit 1
fi

SERVICE_NAME=$1

# 2. Find the container ID based on the Swarm name
# We use 'head -n 1' just in case there are multiple matches
CONTAINER_ID=$(docker ps --filter "name=$SERVICE_NAME" --format "{{.ID}}" | head -n 1)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ ERROR: Could not find any running container matching '$SERVICE_NAME' on this node."
    echo "Run 'docker ps' to verify the container is actually running here."
    exit 1
fi

# 3. Extract the Host PID
HOST_PID=$(docker inspect --format '{{.State.Pid}}' "$CONTAINER_ID")

if [ -z "$HOST_PID" ] || [ "$HOST_PID" == "0" ]; then
    echo "❌ ERROR: Failed to extract a valid Host PID for container $CONTAINER_ID."
    exit 1
fi

echo "======================================================"
echo "🔍 Targeting Container: $SERVICE_NAME"
echo "   Container ID : $CONTAINER_ID"
echo "   Host PID     : $HOST_PID"
echo "======================================================"

# 4. Locate the Python script dynamically (assumes it's in the same folder as this bash script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
TRACKER_SCRIPT="$SCRIPT_DIR/track_dirty_pages.py"

if [ ! -f "$TRACKER_SCRIPT" ]; then
    echo "❌ ERROR: Tracker script not found at $TRACKER_SCRIPT"
    exit 1
fi

# Warn if not running as root, since pagemap requires root privileges
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  WARNING: You did not run this with sudo. The tracker will likely fail with Permission Denied."
fi

# 5. Launch the tracker
python3 "$TRACKER_SCRIPT" "$HOST_PID"
