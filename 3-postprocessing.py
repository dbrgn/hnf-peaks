#!/usr/bin/env python3
import collections
import csv
import sys
from typing import Dict, Tuple, List

class PilotData:
    def __init__(self):
        self.count = 0
        self.peaks = []

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <data-in.csv> <pilots-out.csv>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        data = csv.DictReader(f)

        pilots = collections.defaultdict(lambda: PilotData())  # type: Dict[str, PilotData]

        for line in data:
            pilots[line['top_pilot']].count += 1
            pilots[line['top_pilot']].peaks.append(line['name'])

        with open(sys.argv[2], 'w') as p:
            writer = csv.writer(p)
            writer.writerow(('pilot', 'records', 'peaks'))
            for (pilot, data) in sorted(pilots.items(), key=lambda x: (-x[1].count, x[0])):
                if pilot:
                    writer.writerow((pilot, data.count, ';'.join(data.peaks)))
