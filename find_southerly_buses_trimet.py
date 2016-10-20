#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 3/8/16
"""

import os
import sys
from os import path
import urllib2
import json
import time
import webbrowser
import random
import argparse


VERSION = '0.2.0'

API_KEY_PATH = path.join(path.expanduser('~'), '.API_KEYS')

f = open(API_KEY_PATH, 'r')
keys_list = f.readlines()
f.close()

for item in keys_list:

    if item.startswith('TRIMET_APPID'):
        app_id = item.strip('\n').split('=')[1]
        os.environ['TRIMET_APPID'] = app_id
    elif item.startswith('GOOGLEMAP_API'):
        api_key = item.strip('\n').split('=')[1]
        os.environ['GOOGLEMAP_API'] = api_key

SOURCE = 'http://developer.trimet.org/ws/v2/vehicles/appID/%s' % app_id

# Customize

MY_LAT = 45 + random.uniform(0.4, 0.7)
MY_LON = -122.7005

my_loc = (MY_LON, MY_LAT)

ZOOMED = True
ZOOM = 12
TARGET_DIST = 3.5

zoom_string = '&zoom=' + str(ZOOM)

SIZE = '900x1100'

MARKER_1 = 'color:blue%7Clabel:M%7C%7C' + '%s,%s' % (MY_LAT, MY_LON)

colors = ['black', 'brown', 'green', 'purple', 'yellow', 'gray', 'orange', 'red', 'white', 'darkgreen', 'darkgray',
          'darkbrown']
candidates = set([])

API_KEY = api_key

key_string = '&key=%s' % API_KEY

map = 'https://maps.googleapis.com/maps/api/staticmap?'
map += 'center=%s,%s&size=%s&markers=%s' % (MY_LAT, MY_LON, SIZE, MARKER_1)

if ZOOMED:
    map += zoom_string

print map


def get_data(site=SOURCE):
    u = urllib2.urlopen(site)
    json_data_string = u.read()
    g = open('trimet_bus_data_parsed.json', 'w')
    g.write(json_data_string)
    g.close()


def north_of_me(lat, my_lat):
    if lat > my_lat:
        return True
    else:
        return False


def south_of_me(lat, my_lat):
    if lat < my_lat:
        return True
    else:
        return False


def monitor():
    global map
    u = urllib2.urlopen(SOURCE)

    json_string = u.read()
    data = json.loads(json_string)

    buses = []

    for i in data['resultSet']['vehicle'][:]:
        if i['type'] == 'bus':
            buses.append(i)

    if not buses:
        raise UserWarning('Eh, something wonky there...')
    elif buses:
        for bus in sorted(buses):
            lat = float(bus.get('latitude'))
            lon = float(bus.get('longitude'))

            if north_of_me(lat, MY_LAT):

                bearing = bus.get('bearing')
                busid = bus.get('vehicleID')
                route_num = int(bus.get('routeNumber'))

                if 136 <= bearing <= 225:
                    bus['direction'] = 'Roughly South'
                    #print bus['direction']

                    # print 'buses that are north of me, and are heading south-ish...'

                    print '======\nI think this bus is heading South? \n\tBusId: %s\n' % busid
                    print '\nSign Reads %s' % bus['signMessageLong']
                    print 'route: %s' % route_num
                    print 'bearing: %s ' % bearing

                    candidates.add(busid)

                    dis = lat_dist(lat, MY_LAT)

                    print 'distance: %s Miles\n' % (dis)

                    if dis <= TARGET_DIST:

                        color = colors.pop()

                        candidates.add(color)

                        marker2 = '&markers=color:' + color + '%7Clabel:B%7C' + '%s,%s' % (lat, lon)

                        map.strip(key_string)
                        map += marker2

                elif 46 <= bearing <= 135:
                    bus['direction'] = 'Roughly East'
                    print '\nthe [%s] bus [%s] is north of us, but is heading %s' % (route_num, busid,
                                                                                      bus['direction'])
                elif 226 <= bearing <= 315:
                    bus['direction'] = 'Roughly West'
                    print '\nthe [%s] bus [%s] is north of us, but is heading %s' % (route_num, busid, bus['direction'])
                else:
                    bus['direction'] = 'Roughly North'
                    print '\nthe [%s] bus [%s] is north of us, but is heading %s' % (route_num, busid, bus['direction'])

                print '=' * 8

        map += zoom_string
        map += key_string

        print '-' * 10
        webbrowser.open_new_tab(map)


def open_map(lat, lon):
    map = 'https://maps.googleapis.com/maps/api/staticmap?center='
    map += '%s,%s&size=%s&markers=%s' % (lat, lon, SIZE, MARKER_1)
    map += '&key=%s' % API_KEY
    webbrowser.open_new_tab(map)


def lat_dist(lat1, lat2):
    """approximation of distance (in Miles) between 2 latitudes."""
    return 69 * abs(lat1 - lat2)


while True:
    try:
        monitor()

        if 'darwin' in sys.platform:
            os.system('say "enhance"')

        time.sleep(60)

    except KeyboardInterrupt:

        sys.exit(0)
