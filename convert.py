#!/usr/bin/env python3

from collections import Counter

KINDS = (
    "common",
    "uncommon",
    "rare",
    "rare/mythic rare",
    "land",
    "double faced",
)

class InvalidSet(Exception):
    pass

def make_name(block, name):
    """
    >>> make_name("Shadowmoor", "Eventide")
    "Shadowmoor - Eventide"
    >>> make_name("Shards of Alara", "Shards of Alara")
    "Shards of Alara"
    """
    if not block or block == name: 
        return name
    return "{block} - {name}".format(block=block, name=name)

def generate_card_lists(kind, data):
    """
    >>> generate_card_lists("rare/mythic rare", mtgjson_set)
    {"rare": ["rare1", ... ], "mythic rare": ["mythic1", ...]}
    >>> generate_card_lists("uncommon", mtgjson_set)
    {"uncommon": ["uncommon1", ... ]}
    """

    out = dict()
    if kind == "common":
        out[kind] = [c['name'] for c in data if c['rarity'] == "Common"]
    elif kind == "uncommon":
        out[kind] = [c['name'] for c in data if c['rarity'] == "Uncommon"]
    elif kind == "rare":
        out[kind] = [c['name'] for c in data if c['rarity'] == "Rare"]
    elif kind == "rare/mythic rare":
        out["rare"] = [c['name'] for c in data if c['rarity'] == "Rare"]
        out["mythic rare"] = [c['name'] for c in data if c['rarity'] == "Mythic Rare"]
    elif kind == "double faced":
        out[kind] = [c['name'] for c in data if c['layout'] == "double-faced" and 'manaCost' in c]
    elif kind == "land":
        out[kind] = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
    else:
        out[kind] = []
    return out


def convert_booster(data):
    """
    >>> convert_booster(mtgjson_set)
    {'common': 10, 'land': 1, 'rare/mythic rare': 1, 'uncommon': 3}

    Will throw an exception if the booster is a format that the simulator
    won't understand, e.g. Future Sight
    """
    counter = Counter()
    junk = ("marketing", "checklist")
    for kinds_of_card in data:
        if isinstance(kinds_of_card, str):
            # make is so that we're always dealing with an array
            kinds_of_card = [kinds_of_card]
        junkless = [k for k in kinds_of_card if k not in junk]
        if not junkless:
            # ignore all junk
            continue
        kind = '/'.join(junkless)
        counter.update([kind])
    if any(kind not in KINDS for kind in counter):
        return dict()
    return dict(counter)

def convert_set(data):
    booster = convert_booster(data['booster'])
    out = {
        "name": make_name(data.get('block'), data['name']),
        "booster": booster,
    }
    for kind in booster:
        out.update(generate_card_lists(kind, data['cards']))
    return out

def convert(data):
    types = ('expansion', 'core', 'un')
    sets = [set for set in data.values() if set['type'] in types and 'booster' in set]
    sets.sort(key=lambda set: set.get('releaseDate', 0))
    converted = (convert_set(set) for set in sets[::-1])
    return [set for set in converted if set['booster']]

if __name__ == "__main__":
    import sys
    import json
    sys.stdout.write("mtgJSON(")
    json.dump(convert(json.load(sys.stdin)), sys.stdout)
    sys.stdout.write(")")
