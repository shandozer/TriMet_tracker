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


VERSION = '1.0.0'
LAST_MOD = '10/20/16'

# Customize
program_desc = 'v{}, last-modified {}: \n \
Use this app to reveal any TriMet buses that are North of me AND heading South (in mah way!).'.format(VERSION, LAST_MOD)


def get_parser():
    """
    generic parser uses above info
    """
    parser = argparse.ArgumentParser(description=program_desc)

    parser.add_argument('-d', '--distance', dest='distance', action='store',
                        help="how far away do you want to track?")

    parser.add_argument('-lat', '--latitude', dest='latitude', action='store',
                        help="enter your Latitude if you know it (PDX is approx. 45.49 to 45.55 degrees lat)")

    parser.add_argument('-lon', '--longitude', dest='longitude', action='store',
                        help="enter your Longitude if you know it (PDX is approx. -122.5 to -122.85 degrees lon)")

    return parser


def process_args_for_lat_long_dist(args):

    if args.distance:

        dist = float(args.distance)
        print('\nOption Selected: {}'.format(dist))
    else:
        dist = 3.5

    if args.latitude:

        lat = float(args.latitude)

    else:

        lat = 45 + random.uniform(0.4, 0.60)

    if args.longitude:

        lon = float(args.longitude)

    else:
        lon = -122.7005

    return lat, lon, dist


def main():
    parser = get_parser()
    args = parser.parse_args()

    lat, lon, dist = process_args_for_lat_long_dist(args)

    if args:

        # TODO: convert more statements to Py3 syntax
        print('\nArgs passed: {}'.format(sys.argv[1:]))

    source_url = get_source_site(get_api_keys()[0])

    while True:
        try:
            monitor(source_url, lat, lon, dist)

            if 'darwin' in sys.platform:
                os.system('say "enhance"')

            time.sleep(60)

        except KeyboardInterrupt:

            sys.exit(0)


def get_source_site(app_id):

    trimet_req_url = 'http://developer.trimet.org/ws/v2/vehicles/appID/%s' % app_id

    return trimet_req_url


def get_api_keys(text_file_with_api_keys=None):

    if text_file_with_api_keys:
        filename = path.abspath(text_file_with_api_keys)
    else:
        filename = path.join(path.expanduser('~'), '.API_KEYS')

    filename = path.abspath(filename)

    try:
        with open(filename, 'r') as f:
            keys_list = f.readlines()

            f.close()

        if keys_list:
            for item in keys_list:

                if item.startswith('TRIMET_APPID'):
                    trimet_app_id = item.strip('\n').split('=')[1]
                    os.environ['TRIMET_APPID'] = trimet_app_id
                elif item.startswith('GOOGLEMAP_API'):
                    gmaps_api_key = item.strip('\n').split('=')[1]
                    os.environ['GOOGLEMAP_API'] = gmaps_api_key

        return trimet_app_id, gmaps_api_key

    except IOError, e:
        print('File missing?', e)
    except Exception, e:
        print('Something wrong with your key labels?', e)


def get_data(site):
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


def monitor(source_api_URL, MY_LAT, MY_LON, TARGET_DIST):
    global map

    u = urllib2.urlopen(source_api_URL)

    json_string = u.read()
    data = json.loads(json_string)

    buses = []

    colors = ['black', 'brown', 'green', 'purple', 'yellow', 'gray', 'orange', 'red', 'white', 'darkgreen', 'darkgray',
              'darkbrown']

    candidates = set([])

    ZOOMED = True
    ZOOM = 12

    zoom_string = '&zoom=' + str(ZOOM)

    SIZE = '900x1100'

    MARKER_1 = 'color:blue%7Clabel:M%7C%7C' + '%s,%s' % (MY_LAT, MY_LON)

    key_string = '&key=%s' % get_api_keys()[1]

    map = 'https://maps.googleapis.com/maps/api/staticmap?'
    map += 'center=%s,%s&size=%s&markers=%s' % (MY_LAT, MY_LON, SIZE, MARKER_1)

    if ZOOMED:
        map += zoom_string

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

                # Only process buses with bearing in Southern Range: 90 degree range, straddling the 180-mark
                if 136 <= bearing <= 225:
                    bus['direction'] = 'Roughly South'

                    # print 'buses that are north of me, and are heading south-ish...'

                    print '======\nI think this bus is heading South? \n\tBusId: %s\n' % busid
                    print '\nSign Reads %s' % bus['signMessageLong']
                    print 'route: %s' % route_num
                    print 'bearing: %s ' % bearing

                    candidates.add(busid)

                    dis = lat_dist(lat, MY_LAT)

                    print 'distance: %s Miles\n' % (dis)

                    if dis <= TARGET_DIST:

                        # pros: persistent color for each bus for easier tracking over time
                        # cons: fewer apparent buses, and it will run out of colors eventually -> crashes for now

                        # color = colors.pop()

                        color = random.choice(colors)  # pros: lots of buses // cons: harder to track any 1 bus?

                        candidates.add(color)

                        marker2 = '&markers=color:' + color + '%7Clabel:B%7C' + '%s,%s' % (lat, lon)

                        map.strip(key_string)
                        map += marker2

                # East straddles the 90 degree range

                elif 46 <= bearing <= 135:
                    bus['direction'] = 'Roughly East'
                    print '\nthe [%s] bus [%s] is technically north of us, but is heading %s' % (route_num, busid,
                                                                                                 bus['direction'])
                # Western range straddles 270
                elif 226 <= bearing <= 315:
                    bus['direction'] = 'Roughly West'
                    print '\nthe [%s] bus [%s] is technically north of us, but is heading %s' % (route_num, busid,
                                                                                                 bus['direction'])

                # Northern range is all that's unaccounted for
                else:
                    bus['direction'] = 'Roughly North'
                    print '\nthe [%s] bus [%s] is technically north of us, but is heading %s' % (route_num, busid,
                                                                                                 bus['direction'])

                print '=' * 8

        map += zoom_string
        map += key_string

        print '-' * 10
        webbrowser.open_new_tab(map)


def open_map(lat, lon, api_key, size, marker_one):
    map = 'https://maps.googleapis.com/maps/api/staticmap?center='
    map += '%s,%s&size=%s&markers=%s' % (lat, lon, size, marker_one)
    map += '&key=%s' % api_key
    webbrowser.open_new_tab(map)


def lat_dist(lat1, lat2):
    """approximation of distance (in Miles) between 2 latitudes."""
    return 69 * abs(lat1 - lat2)


if __name__ == '__main__':
    main()
