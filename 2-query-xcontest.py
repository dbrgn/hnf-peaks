#!/usr/bin/env python3

from bs4 import BeautifulSoup
import csv
from datetime import date
import re
from typing import Any, Dict

import psycopg2
import requests


# Config

DB = 'peaks_ch'


# Functions

def query_xcontest(lng: float, lat: float) -> Dict[str, Any]:
    data = {}  # type: Dict[str, Any]

    r = requests.get(f'https://www.xcontest.org/world/en/flights-search/?filter%5Bpoint%5D={lng}+{lat}&filter%5Bradius%5D=200&list%5Bsort%5D=pts&list%5Bdir%5D=down')
    soup = BeautifulSoup(r.text, 'html.parser')

    flights = int(soup.find('form', class_='filter').find('div', class_='wsw').find('p').find('strong').text)
    data['flights'] = flights
    if flights == 0:
        return data

    if flights > 0:
        table = soup.find('table', class_='flights')
        top = table.find('tbody').find_all('tr')[0]
        pilot = top.find('a', class_='plt').text
        distance = top.find('td', class_='km').text
        data['top'] = {
            'pilot': pilot,
            'distance': distance,
        }

    return data


if __name__ == '__main__':
    # Connect
    conn = psycopg2.connect(f'dbname={DB}')

    # Query database
    cur = conn.cursor()
    cur.execute("""
        SELECT id as nid,
               tags->'name' as name,
               tags->'ele',
               ST_AsText(geom::geography)
          FROM nodes
         WHERE tags->'name' is not null
           AND tags->'ele' is not null
           AND cast(tags->'ele' as float) > 1000
         ORDER BY tags->'ele' DESC;
    """)

    # Open CSV file
    filename = 'data-{}.csv'.format(date.today().isoformat())
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('id', 'name', 'ele', 'lng', 'lat', 'flights', 'top_pilot', 'top_dist'))

        # Iterate over keys
        POINT_RE = re.compile(r'^POINT\(([0-9\.]*) ([0-9\.]*)\)$')
        for (nid, name, ele, geog) in cur:
            # Parse point coordinates
            matches = POINT_RE.match(geog)
            assert matches is not None
            lnglat = matches.groups()
            assert lnglat is not None
            lng = float(lnglat[0])
            lat = float(lnglat[1])

            print(f'{name} ({ele}) {lat},{lng}')
            data = query_xcontest(lng, lat)
            print(f'- Flights: {data["flights"]}')
            if 'top' in data:
                top_pilot = data['top']['pilot']
                top_dist = data['top']['distance']
                print(f'- Top flight: {top_pilot} ({top_dist})')
            else:
                top_pilot = ''
                top_dist = ''

            writer.writerow((nid, name, ele, lng, lat, data['flights'], top_pilot, top_dist))
