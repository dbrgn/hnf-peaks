# Hike&Fly Peaks Switzerland

Fetch information about paragliding flights from peaks in Switzerland.

Google Spreadsheet (view only): https://docs.google.com/spreadsheets/d/1rbAsmzIJNCQ0vPOpptib8FrJ6owdlph9MxvN_-6Hi3I/edit?usp=sharing

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
launched from within 300m around the peak:

    ./2-query-xcontest.py

The data will be written to a file called `data-YYYY-MM-DD.csv`.

## 3: Postprocess Data

To calculate some aggregations:

    ./3-postprocessing.py <data-in.csv> <pilots-out.csv>

## License

- Code: GPLv3 or later
- Data: © OpenStreetMap contributors
