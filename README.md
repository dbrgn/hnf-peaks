# Hike&Fly Peaks Switzerland

Fetch information about paragliding flights from alpine peaks.

Map: https://dbrgn.github.io/hnf-peaks/

## Prerequisites

- Bash
- PostgreSQL + PostGIS
- Python 3

## 1: Download OSM Data

This will download the OpenStreetMap database and extract all peaks with an
elevation >1000m:

    ./1-load-osm-data.sh <country>

## 2: Query XContest

This will process all peaks and query XContest for the number of flights that
launched from within 350 m around the peak:

    ./2-query-xcontest.py <country>

The data will be written to a file called `data-YYYY-MM-DD.csv`.

## 3: Postprocess Data

To calculate some aggregations:

    ./3-postprocessing.py <data-in.csv> pilots <pilots-out.csv>

To generate GeoJSON from the data:

    ./3-postprocessing.py <data-in.csv> geojson <geojson-out.json>

## License

- Code: GPLv3 or later
- Data: © OpenStreetMap contributors
