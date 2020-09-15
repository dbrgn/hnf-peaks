#!/bin/bash
set -euo pipefail

OSMOSIS_VERSION=0.48.2

function log() { echo -e "\e[32m$1\e[0m"; }
function loge() { echo -e "\e[31m$1\e[0m"; }
function download() { curl -L -O --fail --show-error "$1"; }

# Determine country
if [ "$#" -ne 1 ]; then
    loge "Usage: $0 <country>"
    loge "Example: $0 switzerland"
    exit 1
fi
COUNTRY=$1
DB="peaks_$COUNTRY"

# Check whether database exists
dbs=$(psql -lqt | cut -d \| -f 1)
if (echo "$dbs" | grep -qw "$DB"); then
    loge "Database \"$DB\" already exists. Please drop it first."
    exit 1
fi
psql="psql -d $DB"

# Download data
DATA=$COUNTRY-latest.osm.pbf
URL="https://download.geofabrik.de/europe/$DATA"
if [ -f "$DATA" ]; then
    log "Data: $DATA already present"
else
    log "Downloading $DATA..."
    download "$URL"
fi

log "Removing and recreating outdir \"$DB\"..."
rm -rf "$DB"
mkdir "$DB"

# Check for osmosis
if [ ! -d "osmosis" ]; then
    if [ ! -f "osmosis-${OSMOSIS_VERSION}.tgz" ]; then
        log "Osmosis not found. Downloading..."
        download https://github.com/openstreetmap/osmosis/releases/download/${OSMOSIS_VERSION}/osmosis-${OSMOSIS_VERSION}.tgz
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
    --write-pgsql-dump directory="$DB" enableBboxBuilder=no enableLinestringBuilder=no nodeLocationStoreType=InMemory keepInvalidWays=no
echo ""

# Create database
log "Creating database \"$DB\"..."
createdb "$DB"
$psql -c "CREATE EXTENSION hstore;"
$psql -c "CREATE EXTENSION postgis;"
$psql -f osmosis/script/pgsnapshot_schema_0.6.sql

# Load data
log "Loading data into database \"$DB\"..."
$psql -c "\copy nodes FROM '$DB/nodes.txt';"
