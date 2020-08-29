#!/usr/bin/env python3
import collections
import csv
import json
import sys
from typing import Dict, List


class PilotData:
    def __init__(self):
        self.count = 0
        self.peaks = []


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


def geojson(argv: List[str], data: csv.DictReader):
    out = {
        'type': 'FeatureCollection',
        'features': [],
    }
    for line in data:
        out['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [line['lng'], line['lat']],
            },
            'properties': {
                'title': line['name'],
                'ele': line['ele'],
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
