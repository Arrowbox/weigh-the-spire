import os
import sys
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--steamapps', default=None, help='Location of steamapps directory')
    parser.add_argument('-r', '--run', default=None, help='Location of single run')
    return parser.parse_args()

def find_runs(steam_path=None):
    if steam_path:
        location = [steam_path]
    elif 'linux' in sys.platform:
        location = ['~', '.steam', 'steam', 'steamapps']
    elif 'darwin' in sys.platform:
        location = ['~', 'Library', 'Application Support', 'Steam', 'SteamApps']
    else:
        location = ['C:', os.sep, 'Program Files', 'Steam', 'steamapps']

    location += ['common', 'SlayTheSpire', 'runs']

    return os.path.expanduser(os.path.join(*location))

def load_run(location):
    with open(location) as fp:
        return json.load(fp)

def load_runs(location):
    runfiles = []
    for path, directories, files in os.walk(location):
        for run in [x for x in files if x.endswith('.run')]:
            filename = os.path.join(path, run)
            runfiles.append(filename)

    runs = []
    for filename in runfiles:
        runs.append(load_run(filename))
    return runs

def parse_floors(run):
    floor_type = {
        'B': 'boss',
        '?':'event',
        'M': 'monster',
        'E': 'elite',
        'T': 'treasure',
        '$': 'merchant',
        'R': 'rest',
        None: 'act'
    }

    floors = {}

    for (i, floor) in enumerate(run['path_per_floor']):
        ftype = floor_type[floor]
        if ftype in floors:
            floors[ftype].append(i+1)
        else:
            floors[ftype] = [i+1]

    return floors

def find_enemies(encounters, floors):
    enemies = {}
    for enemy in [x['enemies'] for x in encounters if x['floor'] in floors]:
        if enemy in enemies:
            enemies[enemy] += 1
        else:
            enemies[enemy] = 1

    return enemies

def find_killed_by(floors, last):
    for floor in floors:
        if floor['floor'] == last:
            return floor.get('enemies', None)

def find_encounters(runs):
    encounters = {
        'boss': {},
        'elite': {}
    }
    deaths = {}

    for run in runs:
        floors = parse_floors(run)
        for enc_type in encounters.keys():
            if enc_type not in floors:
                continue

            update = find_enemies(run['damage_taken'], floors[enc_type])
            for name in update.keys():
                if name in encounters[enc_type]:
                    encounters[enc_type][name] += update[name]
                else:
                    encounters[enc_type][name] = update[name]
        if not run['victory']:
            enemy = find_killed_by(run['damage_taken'], run['floor_reached'])
            if enemy in deaths:
                deaths[enemy] += 1
            else:
                deaths[enemy] = 1

    return {'encounters': encounters, 'deaths': deaths}

def print_encounters(encounters):
    for enc_type in encounters.keys():
        print(enc_type.capitalize())
        for enemy_type in encounters[enc_type].keys():
            print("\t{}:{}".format(enemy_type, encounters[enc_type][enemy_type]))

def print_deaths(deaths):
    print("Killed by:")
    for enemy in deaths.keys():
        if enemy:
            print("\t{}:{}".format(enemy, deaths[enemy]))

def main():
    args = parse_args()

    location = find_runs(args.steamapps)
    print("Runs path: {}".format(location))

    if args.run:
        runs = [load_run(args.run)]
    else:
        runs = load_runs(location)
    print("Found {} runs".format(len(runs)))

    encounters = find_encounters(runs)

    print_encounters(encounters['encounters'])
    print_deaths(encounters['deaths'])

if __name__ == '__main__':
    main()
