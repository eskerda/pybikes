#!/usr/bin/env python

"""
Generates a md report based on the exported JSON results of a pytest run

$ python utils/report.py .report.json > report.md
"""

import os
import re
import sys
import html
import json
import argparse
from pprint import pformat

from jinja2 import Template

from pybikes.data import _iter_data
from pybikes.data import _datafile_traversor


TEMPLATES_PATH = os.path.dirname(os.path.realpath(__file__))
FULL_TEMPLATE_PATH = "%s/report.tpl.md" % TEMPLATES_PATH
SUMMARY_TEMPLATE_PATH = "%s/summary.tpl.md" % TEMPLATES_PATH

parser = argparse.ArgumentParser()
parser.add_argument('report', type=argparse.FileType('r'))
parser.add_argument('--template', default=FULL_TEMPLATE_PATH)
parser.add_argument('--out', type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('--summary', action='store_true', default=False)
args = parser.parse_args()


def format_duration(duration):
    seconds = int(duration)
    ms = int((duration - seconds) * 1000)
    if seconds:
        return "%ds %sms" % (seconds, ms)
    return "%sms" % ms


def format_outcome(outcome):
    sym = "✅" if outcome in ['passed'] else "❌"
    return sym


def format_traceback(report):
    fmt_trace = [
        'File "%s", line %d, %s' % (t['path'], t['lineno'], t['message'])
        for t in reversed(report['call']['traceback'])
    ]
    fmt_trace.append("\n" + report['call']['crash']['message'])

    return '\n'.join(fmt_trace)


def parse_report(report):
    for test in report['tests']:
        # only parse instance update tests
        if not test['keywords'][0].startswith('test_update['):
            continue
        for keyword in test['keywords']:
            match = re.search(r'test_update\[(.*)\.(.*)\:\:(.*)\]$', keyword)
            if not match:
                continue

            mod, cls, tag = match.groups()

            yield (mod, cls, tag, test)
            break


def generate_report(report, template):
    report_by_tag = {tag: test for _, _, tag, test in parse_report(report)}

    systems = []
    for fname, data in _iter_data():
        instances = data.get('instances')

        # aggregate by class
        classes = {}
        for cls, instance in _datafile_traversor(data['class'], instances):
            if cls not in classes:
                classes[cls] = []
            classes[cls].append(instance)

        _classes = []

        for cls, instances in classes.items():
            _instances = []
            for instance in instances:
                tag = instance['tag']
                if tag not in report_by_tag:
                    continue
                _instances.append({
                      'tag': tag,
                      'instance': instance,
                      'report': report_by_tag[tag],
                })

            if not _instances:
                continue

            passed = filter(lambda i: i['report']['outcome'] in ['passed'], _instances)
            n_passed = len(list(passed))
            health = n_passed / len(_instances)

            _classes.append({
                'name': cls,
                'instances': _instances,
                'health': n_passed / len(_instances),
                'failed': len(_instances) - n_passed,
                'passed': n_passed,
                'total': len(_instances),
            })

        if not _classes:
            continue

        health = sum(map(lambda c: c['health'], _classes)) / len(_classes)
        passed = sum(map(lambda c: c['passed'], _classes))
        failed = sum(map(lambda c: c['failed'], _classes))
        systems.append({
            'name': data['system'],
            'classes': _classes,
            'passed': passed,
            'failed': failed,
            'total': passed + failed,
            'health': health,
        })

    sorted_systems = sorted(systems, key=lambda s: s['health'])

    passed = sum(map(lambda s: s['passed'], systems))
    failed = sum(map(lambda s: s['failed'], systems))
    total = passed + failed

    # Create one big massive geojson file
    networks = {
        'type': "FeatureCollection",
        'features': [],
    }

    for system in sorted_systems:
        for cls in system['classes']:
            for instance in cls['instances']:
                networks['features'].append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            instance['instance']['meta']['longitude'],
                            instance['instance']['meta']['latitude'],
                        ],
                    },
                    'properties': {
                        'name': instance['instance']['meta'].get('name'),
                        'type': 'network',
                        'tag': instance['tag'],
                        'outcome': instance['report']['outcome'],
                        'failed': instance['report']['outcome'] == 'failed',
                        'traceback': html.escape(instance['report']['call']['longrepr']) if instance['report']['outcome'] == 'failed' else '',
                    }
                })

                if 'user_properties' not in instance['report']:
                    continue

                features = instance['report']['user_properties'][0]['geojson']['features']
                for feature in features:
                    feature['properties']['type'] = 'station'
                    feature['properties']['tag'] = instance['tag']

                    networks['features'].append(feature)


    tpl = Template(template, trim_blocks=True, lstrip_blocks=True)
    return tpl.render(
        health={'passed': passed, 'failed': failed, 'total': total},
        systems=sorted_systems,
        geojson=networks,
        version=report['environment']['Python'],
        pformat=pformat,
        json=json,
        len=len,
        int=int,
        format_duration=format_duration,
        format_outcome=format_outcome,
        format_traceback=format_traceback,
    )


if __name__ == "__main__":
    report = json.loads(args.report.read())
    if args.summary:
        template = open(SUMMARY_TEMPLATE_PATH).read()
    else:
        template = open(args.template).read()
    report_md = generate_report(report, template)

    args.out.write(report_md)
