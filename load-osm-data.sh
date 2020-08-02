#!/bin/bash
set -euo pipefail

OSMOSIS_VERSION=0.48.2

function log() { echo -e "\e[32m$1\e[0m"; }
function loge() { echo -e "\e[31m$1\e[0m"; }

# Parse arguments
if [ "$#" -ne 1 ]; then
    echo "Download and parse OSM file."
    echo ""
    echo "Usage: $0 <db_name>"
    echo "Example: $0 osm"
    exit 1
fi
db=$1

# Check whether database exists
dbs=$(psql -lqt | cut -d \| -f 1)
if (echo "$dbs" | grep -qw "$db"); then
    loge "Database \"$db\" already exists. Please drop it first."
    exit 1
fi
psql="psql -d $db"

# Download data
DATA=switzerland-latest.osm.pbf
URL="https://download.geofabrik.de/europe/$DATA"
if [ -f "$DATA" ]; then
    log "Data: $DATA already present"
else
    log "Downloading $DATA..."
    curl -L -O $URL
fi

log "Removing and recreating outdir \"$db\"..."
rm -rf "$db"
mkdir "$db"

# Check for osmosis
if [ ! -d "osmosis" ]; then
    if [ ! -f "osmosis-${OSMOSIS_VERSION}.tgz" ]; then
        log "Osmosis not found. Downloading..."
        curl -L -O https://github.com/openstreetmap/osmosis/releases/download/${OSMOSIS_VERSION}/osmosis-${OSMOSIS_VERSION}.tgz
    fi
    mkdir -p osmosis/
    tar xfz osmosis-${OSMOSIS_VERSION}.tgz -C osmosis/
fi

# Extract data
# Note: When loading ways, do not exclude nodes! Otherwise the bbox cannot be properly calculated.
log "Extracting data..."
osmosis/bin/osmosis \
    --read-pbf "$DATA" \
        --tag-filter reject-relations \
        --tag-filter reject-ways \
        --node-key-value keyValueList=natural.peak \
    --log-progress interval=5 \
    --write-pgsql-dump directory="$db" enableBboxBuilder=no enableLinestringBuilder=no nodeLocationStoreType=InMemory keepInvalidWays=no
echo ""

# Create database
log "Creating database \"$db\"..."
createdb "$db"
$psql -c "CREATE EXTENSION hstore;"
$psql -c "CREATE EXTENSION postgis;"
$psql -f osmosis/script/pgsnapshot_schema_0.6.sql

# Load data
log "Loading data into database \"$db\"..."
$psql -c "\copy nodes FROM '$db/nodes.txt';"
