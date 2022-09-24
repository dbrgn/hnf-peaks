#!/usr/bin/env python3

from dataclasses import dataclass
import csv
from datetime import date
import os
import re
import sys
from typing import Any, Optional

from bs4 import BeautifulSoup
import psycopg2
import requests


# Config

RADIUS = 350
XCONTEST_USER = os.environ.get('XCONTEST_USER', 'dbrgn')
XCONTEST_PASS = os.environ.get('XCONTEST_PASS')
assert XCONTEST_PASS, 'Did not find XCONTEST_PASS env var'


# Data classes

@dataclass
class TopFlight:
    pilot: str
    distance: float


@dataclass
class PeakData:
    flights: int
    top: Optional[TopFlight] = None


# Functions

def query_xcontest(session: requests.Session, lng: float, lat: float) -> PeakData:
    url = f'https://www.xcontest.org/world/en/flights-search/?filter%5Bpoint%5D={lng}+{lat}&filter%5Bradius%5D={RADIUS}&list%5Bsort%5D=pts&list%5Bdir%5D=down'
    r = session.get(url, headers={
        'user-agent': 'github.com/dbrgn/hnf-peaks',
    })
    soup = BeautifulSoup(r.text, 'html.parser')

    flights = int(soup.find('form', class_='filter').find('div', class_='wsw').find('p').find('strong').text)  # type: ignore
    data = PeakData(flights=flights)
    if flights == 0:
        return data

    if flights > 0:
        table = soup.find('table', class_='flights')
        top = table.find('tbody').find_all('tr')[0]  # type: ignore
        pilot = top.find(class_='plt').text
        distance = top.find('td', class_='km').text
        data.top = TopFlight(pilot=pilot, distance=distance)

    return data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <country>')
        sys.exit(1)

    country = sys.argv[1].lower()

    # Connect
    conn = psycopg2.connect(f'dbname=peaks_{country}')

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

    # Authenticate against XContest
    session = requests.Session()
    auth_response = session.post('https://www.xcontest.org/world/en/', data={
        'login[username]': XCONTEST_USER,
        'login[password]': XCONTEST_PASS,
        'login[persist_login]': 'Y',
    })
    assert auth_response.status_code == 200, f'Auth failed, status code {auth_response.status_code}'
    assert XCONTEST_USER in auth_response.text, 'Auth failed, username not found in auth response body'

    # Open CSV file
    filename = 'data-{}-{}.csv'.format(country, date.today().isoformat())
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
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
            data = query_xcontest(session, lng, lat)
            print(f'- Flights: {data.flights}')
            if data.top:
                top_pilot = data.top.pilot
                top_dist = str(data.top.distance)
                print(f'- Top flight: {top_pilot} ({top_dist})')
            else:
                top_pilot = ''
                top_dist = ''

            writer.writerow((nid, name, ele, lng, lat, data.flights, top_pilot, top_dist))
