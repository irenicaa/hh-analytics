#!/usr/bin/env python3

import logging
import functools
import argparse
import collections
import fileinput
import json
import csv
import re

import requests
import box

TAX = 0.13
SPECIALIZATION_COLUMNS_INDEXES = {
    'salary.average': 1,
    'salary.minimum': 2,
    'salary.maximum': 3,
    'number': 4,
}

def save_stats(args, stats, filename_parts, headers, row_handler, sort_key_getter):
    stats_rows = []
    for number, stats_row in enumerate(stats.items()):
        logging.info('process the stats row #%d', number)
        name, data = stats_row
        stats_rows.append(row_handler(name, data))
    stats_rows.sort(key=sort_key_getter)

    if args.query:
        filename_parts.append(args.query.pattern)
    if args.handicapped:
        filename_parts.append('handicapped')
    if args.remote:
        filename_parts.append('remote')
    if args.no_experience:
        filename_parts.append('no_experience')
    filename = '.'.join(filename_parts + ['csv'])

    with open(filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        for number, stats_row in enumerate(stats_rows):
            logging.info('output the stats row #%d', number)
            csv_writer.writerow(stats_row)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--query', type=lambda query: re.compile(query, re.I))
parser.add_argument('-H', '--handicapped', action='store_true')
parser.add_argument('-r', '--remote', action='store_true')
parser.add_argument('-e', '--no_experience', action='store_true')
parser.add_argument('--data_1', required=True, choices=['profareas', 'specializations'])
parser.add_argument('-s', '--sort', required=True, choices=SPECIALIZATION_COLUMNS_INDEXES.keys())
parser.add_argument('--data_2', choices=['areas', 'cities'])
args = parser.parse_args()

currencies = {}
dictionaries = box.Box(requests.get('https://api.hh.ru/dictionaries').json())
for currency in dictionaries.currency:
    currencies[currency.code] = currency.rate

specializations = collections.defaultdict(list)
cities = collections.Counter()
for number, line in enumerate(fileinput.input(files=[])):
    logging.info('process the vacancy #%d', number)
    try:
        if args.query and args.query.search(line) is None:
            continue

        vacancy = box.Box(json.loads(line))
        if args.handicapped and not vacancy.accept_handicapped:
            continue
        if args.remote and vacancy.schedule.id != 'remote':
            continue
        if args.no_experience and vacancy.experience.id != 'noExperience':
            continue

        if args.data_2 == 'areas':
            cities[vacancy.area.name] += 1
        elif args.data_2 == 'cities' and vacancy.address and vacancy.address.city:
            cities[vacancy.address.city] += 1

        salary = None
        if vacancy.salary:
            if vacancy.salary.to:
                salary = vacancy.salary.to
            # override the salary with its minimum, if there are specified both limits
            if vacancy.salary['from']:
                salary = vacancy.salary['from']
        if not salary:
            continue

        salary /= currencies[vacancy.salary.currency]
        if vacancy.salary.gross:
            salary -= salary * TAX

        for specialization in vacancy.specializations:
            if args.data_1 == 'profareas':
                name = specialization.profarea_name
            else:
                name = '{} / {}'.format(specialization.profarea_name, specialization.name)
            specializations[name].append(salary)
    except Exception as exception:
        logging.error('error: %s', exception)

save_stats = functools.partial(save_stats, args)
if specializations:
    logging.info('save the %s stats', args.data_1)
    save_stats(
        stats=specializations,
        filename_parts=[args.data_1, args.sort],
        headers=['Name', 'Salary, average', 'Salary, minimum', 'Salary, maximum', 'Number'],
        row_handler=lambda name, salaries: [
            name,
            round(sum(salaries) / len(salaries)),
            round(min(salaries)),
            round(max(salaries)),
            len(salaries),
        ],
        sort_key_getter=lambda specialization_row: [
            -specialization_row[SPECIALIZATION_COLUMNS_INDEXES[args.sort]],
            specialization_row[0].lower(),
        ],
    )
if cities:
    logging.info('save the %s stats', args.data_2)
    save_stats(
        stats=cities,
        filename_parts=[args.data_2],
        headers=['Name', 'Number'],
        row_handler=lambda name, number: [name, number],
        sort_key_getter=lambda city_row: [-city_row[1], city_row[0].lower()],
    )
