#!/bin/bash
set -e

echo "======================================================"
echo " Initiating DeathStarBench wrk2 Workload Generator"
echo "======================================================"

# Configuration Variables 
# You can pass the Gateway IP as the first argument, or it defaults to node-0
GATEWAY_IP=${1:-"node-0"} 
GATEWAY_PORT="5000"

# Tuning parameters (Default: 1000 requests/sec for 60 seconds)
RATE=${2:-1000}       # Target Requests Per Second (RPS)
CONNECTIONS=${3:-256} # Number of open HTTP connections
THREADS=${4:-16}      # Number of wrk2 OS threads (match this to your node's CPU cores)
DURATION=${5:-"60s"}  # How long to run the experiment

# Paths (Assuming you run this from the hotelReservation directory)
WRK_BIN="../wrk2/wrk"
LUA_SCRIPT="./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua"
TARGET_URL="http://${GATEWAY_IP}:${GATEWAY_PORT}"

# 1. Sanity check: Ensure wrk2 is compiled
if [ ! -f "$WRK_BIN" ]; then
    echo "❌ ERROR: wrk2 executable not found at $WRK_BIN"
    echo "Please run 'make' inside the DeathStarBench/wrk2 directory first."
    exit 1
fi

echo "Target URL  : $TARGET_URL"
echo "Workload    : $LUA_SCRIPT"
echo "Parameters  : Rate=$RATE RPS | Conn=$CONNECTIONS | Threads=$THREADS | Time=$DURATION"
echo "------------------------------------------------------"
echo "Firing traffic... (Please wait $DURATION)"
echo ""

# 2. Execute wrk2
$WRK_BIN -D exp \
    -t "$THREADS" \
    -c "$CONNECTIONS" \
    -d "$DURATION" \
    -L \
    -s "$LUA_SCRIPT" \
    "$TARGET_URL" \
    -R "$RATE"

echo ""
echo "======================================================"
echo "✅ Workload complete."
echo "======================================================"
