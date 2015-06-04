# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import string

import requests

import sys

MAIN = 'https://gw.cyclocity.fr/3311a6cea2e49b10/'

ACTIONS = {
    'cities': 'contracts/full?token={token}',
    'token': 'token/key/b885ab926fdca7dbfbf717084fb36b5f',
    'availability': 'availability/{city}/stations/state/?token={token}',
    'availabitity_by_geo': 'availability/{city}/stations/proximity/{what}?lat={lat}&lng={lng}&maxRes=10000&min=1&token={token}'
}

TOKEN = None

def getUrl(action, **args):
    return '%s%s' % (MAIN, ACTIONS[action].format(**args))

def call(action, **args):
    if 'token' not in args and TOKEN is not None:
        args['token'] = TOKEN
    url = getUrl(action, **args)
    r = requests.get(url)
    return r.json()

def getToken():
    data = call('token')
    return data['token']

def listCities():
    cities = call('cities', token = TOKEN)
    print '--- %d Cities ---' % len(cities)
    for idx, city in enumerate(cities):
        print '[%d] %s - %s' % (idx, city['name'], city['code'])
    return cities

def listActions():
    print '--- Actions ---'
    res = []
    for idx, action in enumerate(MENU_ACTIONS):
        print '%d %s' % (idx, action)
        res.append(action)
    number = input('>> Select an action: ')
    action = res[number]
    return MENU_ACTIONS[action]

def getParams(action):
    iterparams = string.Formatter().parse(ACTIONS[action])
    params = [x[1] for x in iterparams if x[1] is not None and x[1] != 'token' and x[1] != 'city']
    user_input = {}
    for p in params:
        stuff = str(raw_input('>> %s: ' % p))
        user_input[p] = stuff
    return user_input

def quit(** args):
    sys.exit(0)

def get_everything(city):
    n_stations = count_stations(city)
    minLat = city['viewPort']['minLat']
    minLng = city['viewPort']['minLng']
    maxLat = city['viewPort']['maxLat']
    maxLng = city['viewPort']['maxLng']
    square = [0.001, 0.001]
    square[0] = float(raw_input('>> Select latitude box: '))
    square[1] = float(raw_input('>> Select longitude box: '))
    if (minLat > maxLat):
        square[0] = square[0] * -1
    if (minLng > maxLng):
        square[1] = square[1] * -1

    c_square_lat = minLat
    c_square_lng = minLng
    inRange = True
    geosquares = []
    all_stations = {}
    print 'From %s to %s' % ([minLat, minLng], [maxLat, maxLng])
    print 'Using %s' % square
    inc = 0
    print 'Recalculating splines...'
    while(inRange):
        geosquares.append([c_square_lat, c_square_lng])
        c_square_lng = c_square_lng + square[1]
        if (c_square_lng > maxLng + square[1]):
            c_square_lng = minLng
            c_square_lat = c_square_lat + square[0]
        inRange = c_square_lat < maxLat + square[0]
    print "%d Geo Squares calculated" % len(geosquares)
    nothing = raw_input('Is it ok?')
    if nothing == 'no':
        return
    for idx, gsquare in enumerate(geosquares):
        stations = call('availabitity_by_geo', city = city['code'], what = 'bike', lat = gsquare[0], lng = gsquare[1])
        added = 0
        for station in stations:
            if station['station']['nb'] not in all_stations:
                all_stations[station['station']['nb']] = station
                added = added + 1
        if (added > 0):
            sys.stdout.flush()
            sys.stdout.write('\r[%d%%] Got %d stations of %d' % (idx * 100 / len(geosquares), len(all_stations), n_stations))
        sys.stdout.write('.')

    print len(all_stations)

def count_stations(city):
    stations = call('availability', city = city['code'])
    print '%d stations in %s' % (len(stations['ststates']), city['name'])
    print stations
    return len(stations['ststates'])

MENU_ACTIONS = {
    'quit': quit,
    'get_everything': get_everything,
    'count_stations': count_stations,
}


if TOKEN is None:
    TOKEN = getToken()

cities = listCities()
number = input('>> Please, select your city: ')
city = cities[number]
print('%s selected' % city['name'])
while (True):
    action = listActions()
    action(city)


