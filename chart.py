#!/usr/bin/env python3

import argparse
import csv
import itertools
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot

LABEL_LENGTH = 10
BAR_WIDTH = 0.75
BAR_COLOR = '#3286aa'

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--column', required=True, type=int, choices=range(1, 5))
parser.add_argument('-l', '--row-limit', type=int)
parser.add_argument('-x', '--xlabel')
parser.add_argument('-y', '--ylabel', required=True)
parser.add_argument('input', nargs=1)
args = parser.parse_args()

labels, data = [], []
filename = args.input[0]
with open(filename, newline='') as csv_file:
    csv_reader = csv.reader(csv_file)
    row_limit = args.row_limit + 1 if args.row_limit is not None else None
    for csv_row in itertools.islice(csv_reader, 1, row_limit):
        label = csv_row[0]
        if len(label) > LABEL_LENGTH:
            label = label[:LABEL_LENGTH] + '...'
        labels.append(label)
        data.append(int(csv_row[args.column]))

figure, axes = matplotlib.pyplot.subplots()
indexes = list(range(len(data)))
bars = axes.bar(indexes, data, BAR_WIDTH, color=BAR_COLOR)
axes.set_xticks(indexes)
axes.set_xticklabels(labels, rotation=90)
if args.xlabel:
    axes.set_xlabel(args.xlabel)
axes.set_ylabel(args.ylabel)

figure.tight_layout()
filename_root = os.path.splitext(filename)[0]
figure.savefig(filename_root + '.png')
