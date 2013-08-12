# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import os
import sys
import time
import json
import argparse

from slugify import slugify
import pybikes

api_key = 'ace81338b73283277ddfe54c217ab965ac93cb50'

description = 'Extract cyclocity instances'

parser = argparse.ArgumentParser(description = description)

parser.add_argument('-o', metavar = "output", dest = "output", 
                    type = argparse.FileType('w'), default = sys.stdout, 
                    help="Output file")

parser.add_argument('-v', action="store_true", dest = 'verbose', 
                    default = False, help="Verbose output for debugging (no progress)")

parser.add_argument('--proxy', metavar = "host:proxy", dest = 'proxy', 
                    default = None, help="Use host:port as a proxy for site calls")

parser.add_argument('--httpsproxy', metavar = "host:proxy", dest = 'httpsproxy', 
                    default = None, help="Use host:port as an HTTPS proxy for site calls")

args = parser.parse_args()

scraper = pybikes.utils.PyBikesScraper()

proxies = {}

sysdef = {
    "system": "cyclocity",
    "class": "Cyclocity",
    "instances": []
}

def clearline(length):
    clearline = "\r" + "".join([" " for i in range(length)])
    sys.stderr.flush()
    sys.stderr.write(clearline)
    sys.stderr.flush()

def print_status(i, total, status):
    progress = "".join(["#" for step in range(i)]) + \
               "".join([" " for step in range(total-i)])
    status_pattern = "\r{0}/{1}: [{2}] {3}"
    output = status_pattern.format(i, total, progress, status)
    sys.stderr.flush()
    sys.stderr.write(unicode(output))
    sys.stderr.flush()
    if (i == total):
        sys.stderr.write('\n')
    return len(output)

def main():
    if args.proxy is not None:
        proxies['http'] = args.proxy
        scraper.enableProxy()

    if args.httpsproxy is not None:
        proxies['https'] = args.httpsproxy
        scraper.enableProxy()

    scraper.setProxies(proxies)

    services = pybikes.Cyclocity.get_contracts(api_key, scraper)
    lastlen = 0
    for i, service in enumerate(services):
        sysdef['instances'].append(
            {
                'tag': slugify(service['commercial_name']),
                'contract': service['name'],
                'meta': {
                    'name': service['commercial_name'],
                    'country': service['country_code']
                }
            }
        )
        clearline(lastlen)
        lastlen = print_status(i+1, len(services), \
                        "Testing %s" % repr(service['name']))

    output = json.dumps(sysdef, sort_keys = False, indent = 4)
    args.output.write(output)
    args.output.write('\n')
    args.output.close()

if __name__ == "__main__":
    main()