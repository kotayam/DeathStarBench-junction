#!/bin/bash
set -e

# Default Configuration Values
GATEWAY_IP="node-0"
GATEWAY_PORT="5000"
RATE=1000
CONNECTIONS=256
THREADS=16
DURATION="60s"

# Help menu function
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -i  Gateway IP/Hostname (default: $GATEWAY_IP)"
    echo "  -r  Target Requests Per Second (default: $RATE)"
    echo "  -c  Number of open HTTP connections (default: $CONNECTIONS)"
    echo "  -t  Number of wrk2 OS threads (default: $THREADS)"
    echo "  -d  Duration of the test (default: $DURATION)"
    echo "  -h  Show this help message"
    exit 1
}

# Parse command-line flags
while getopts "i:r:c:t:d:h" opt; do
    case ${opt} in
        i ) GATEWAY_IP=$OPTARG ;;
        r ) RATE=$OPTARG ;;
        c ) CONNECTIONS=$OPTARG ;;
        t ) THREADS=$OPTARG ;;
        d ) DURATION=$OPTARG ;;
        h ) usage ;;
        \? ) echo "Invalid option: -$OPTARG" >&2; usage ;;
    esac
done

echo "======================================================"
echo " Initiating DeathStarBench wrk2 Workload Generator"
echo "======================================================"

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
