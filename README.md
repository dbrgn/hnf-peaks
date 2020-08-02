# Hike&Fly Peaks Switzerland

Fetch information about paragliding flights from peaks in Switzerland.

## Prerequisites

- Bash
- PostgreSQL + PostGIS
- Python 3

## 1: Download OSM Data

This will download the OpenStreetMap database and extract all peaks with an
elevation >1000m:

    ./1-load-osm-data.sh

## 2: Query XContest

This will process all peaks and query XContest for the number of flights that
launched from within 200m around the peak:

    ./2-query-xcontest.py

The data will be written to a file called `data-YYYY-MM-DD.csv`.

## License

- Code: GPLv3 or later
- Data: © OpenStreetMap contributors