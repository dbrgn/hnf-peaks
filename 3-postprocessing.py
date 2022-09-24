#!/usr/bin/env python3
import collections
import csv
from dataclasses import dataclass, field
import json
import sys
from typing import Dict, List, Literal, Tuple, TypedDict


@dataclass
class PilotData:
    count: int = 0
    peaks: List[str] = field(default_factory=list)


def pilots(argv: List[str], data: csv.DictReader):
    pilots = collections.defaultdict(lambda: PilotData())  # type: Dict[str, PilotData]

    for line in data:
        pilots[line['top_pilot']].count += 1
        pilots[line['top_pilot']].peaks.append(line['name'])

    with open(sys.argv[3], 'w') as p:
        writer = csv.writer(p)
        writer.writerow(('pilot', 'records', 'peaks'))
        for (pilot, pdata) in sorted(pilots.items(), key=lambda x: (-x[1].count, x[0])):
            if pilot:
                writer.writerow((pilot, pdata.count, ';'.join(pdata.peaks)))


class Geometry(TypedDict):
    type: Literal['Point']
    coordinates: Tuple[str, str]


class TopFlight(TypedDict):
    pilot: str
    dist: str


class Properties(TypedDict):
    title: str
    ele: str
    flights: int
    top: TopFlight
    icon: str


class Feature(TypedDict):
    type: Literal['Feature']
    geometry: Geometry
    properties: Properties


class FeatureCollection(TypedDict):
    type: Literal['FeatureCollection']
    features: List[Feature]


def geojson(argv: List[str], data: csv.DictReader):
    out: FeatureCollection = {
        'type': 'FeatureCollection',
        'features': [],
    }
    for line in data:
        assert line['lng'], 'longitude missing'
        assert line['lat'], 'latitude missing'
        out['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (line['lng'], line['lat']),
            },
            'properties': {
                'title': line['name'],
                'ele': line['ele'],
                'lat': float(line['lat']),
                'flights': int(line['flights']),
                'top': {
                    'pilot': line['top_pilot'],
                    'dist': line['top_dist'],
                },
                'icon': 'marker',
            },
        })

    with open(argv[3], 'w') as f:
        f.write(json.dumps(out, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 4 or sys.argv[2] not in ['pilots', 'geojson']:
        print('Usage:')
        print(f'  {sys.argv[0]} <data-in.csv> pilots <pilots-out.csv>')
        print(f'  {sys.argv[0]} <data-in.csv> geojson <geojson-out.json>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        data = csv.DictReader(f)

        if sys.argv[2] == 'pilots':
            pilots(sys.argv, data)
        elif sys.argv[2] == 'geojson':
            geojson(sys.argv, data)
