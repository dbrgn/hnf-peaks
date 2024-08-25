# Hike&Fly Peaks Switzerland

Fetch information about paragliding flights from alpine peaks.

Map: https://dbrgn.github.io/hnf-peaks/

## Prerequisites

- Bash
- PostgreSQL + PostGIS
- Python 3
- The following Python packages: beautifulsoup4, psycopg2

## 0: Start services

The easiest way to run PostGIS is through Docker:

    docker run -d --name hnf-peaks-pg \
          -e POSTGRES_USER=$(id -u -n) \
          -e POSTGRES_HOST_AUTH_METHOD=trust \
          -p 127.0.0.1:5432:5432 \
          docker.io/postgis/postgis:16-3.4-alpine

## 1: Download OSM Data

This will download the OpenStreetMap database and extract all peaks with an
elevation >1000m:

    ./1-load-osm-data.sh <country>

## 2: Query XContest

This will process all peaks and query XContest for the number of flights that
launched from within 350 m around the peak:

    export XCONTEST_USER=...
    export XCONTEST_PASS=...
    ./2-query-xcontest.py <country>

The data will be written to a file called `data-YYYY-MM-DD.csv`.

**WARNING:** X-Contest does rate limiting, so unless you are whitelisted by
them, you will probably get blocked after a while. Furthermore, do not run this
command on the evening of a hammer day, choose a time when XContest is not
busy.

## 3: Postprocess Data

To calculate some aggregations:

    ./3-postprocessing.py <data-in.csv> pilots <pilots-out.csv>

To generate GeoJSON from the data:

    ./3-postprocessing.py <data-in.csv> geojson <geojson-out.json>

## License

- Code: GPLv3 or later
- Data: © OpenStreetMap contributors
