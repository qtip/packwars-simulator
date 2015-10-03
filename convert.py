#!/usr/bin/env python3

"""
{"KEY":{
        "name": "Name",
        "mythics": ["a", "b", ...],
        "rares": ["a", "b", ...],
        "uncommons": ["a", "b", ...],
        "commons": ["a", "b", ...]
    }, ...}
"""

def make_name(block, name):
    if not block or block == name: 
        return name
    return "{block} - {name}".format(block=block, name=name)

def convert_set(data):
    mythics = list({card['name'] for card in data['cards'] if card['rarity'] == "Mythic Rare"})
    rares = list({card['name'] for card in data['cards'] if card['rarity'] == "Rare"})
    uncommons = list({card['name'] for card in data['cards'] if card['rarity'] == "Uncommon"})
    commons = list({card['name'] for card in data['cards'] if card['rarity'] == "Common"})
    mythics.sort()
    rares.sort()
    uncommons.sort()
    commons.sort()
    out = {
        "name": make_name(data.get('block'), data['name']),
        "mythics": mythics,
        "rares": rares,
        "uncommons": uncommons,
        "commons": commons,
    }
    return out

def convert(data):
    sets = [set for set in data.values() if set['type'] == 'expansion']
    sets.sort(key=lambda set: set.get('releaseDate', 0))
    return [convert_set(set) for set in sets[::-1]]

if __name__ == "__main__":
    import sys
    import json
    sys.stdout.write("mtgJSON(")
    json.dump(convert(json.load(sys.stdin)), sys.stdout)
    sys.stdout.write(")")
