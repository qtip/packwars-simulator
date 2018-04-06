#!/usr/bin/env python3
import datetime
from itertools import groupby

class ProbabilityTable:
    """
    Given a tree with values at the leaves in the form of nested lists,
    return a Dict where the key is a leaf value and the value is the probability
    of choosing that leaf from a unformly distributed random walk of the tree.

    >>> ProbabilityTable.from_tree(['A', 'B']).to_packwars_dict() == \
    {'A': 0.5, 'B': 0.5}
    True
    >>> ProbabilityTable.from_tree(['A', ['X', 'Y']]).to_packwars_dict() == \
    {'Y': 0.25, 'X': 0.25, 'A': 0.5}
    True
    >>> ProbabilityTable.from_tree(['common']).to_packwars_dict()
    {'common': 1.0}
    >>> ProbabilityTable.from_tree([]).to_packwars_dict()
    {}
    >>> ProbabilityTable.from_tree("AB").to_packwars_dict()
    Traceback (most recent call last):
        ...
    AssertionError: Must be a nested-list tree
    """

    def __init__(self, table=None):
        self.table = table if table else {}

    @classmethod
    def from_tree(cls, tree):
        assert not isinstance(tree, str), "Must be a nested-list tree"

        table = {}
        def _add_to_table(node, unity):
            if not node:
                return
            elif isinstance(node, str):
                # leaf node
                leaf = node
                table[leaf] = table.get(leaf, 0.0) + unity
            else:
                # sub-tree
                sub_tree = node
                sub_unity = unity / len(sub_tree)
                for sub_node in sub_tree:
                    _add_to_table(sub_node, sub_unity)
        _add_to_table(tree, 1.0)
        return cls(table=table)

    def keys(self):
        return self.table.keys()

    def pop(self, *args, **kwargs):
        self.table.pop(*args, **kwargs)

    def to_packwars_dict(self):
        return self.table

class BoosterFormat:
    JUNK = {"marketing", "checklist", "token"}
    def __init__(self, probability_tables=[]):
        self.probability_tables = probability_tables
        for table in probability_tables[::-1]:
            for junk in self.JUNK:
                table.pop(junk, None)
            if not table:
                probability_tables.remove(table)

    @classmethod
    def from_mtgjson_dict(cls, data):
        probability_tables = []
        for tree in data:
            if isinstance(tree, str):
                # mtgjson has either strings or arrays here,
                # make them all arrays
                tree = [tree]
            probability_tables.append(ProbabilityTable.from_tree(tree))
        return cls(probability_tables)

    def required_card_types(self):
        card_types = set()
        for probability_table in self.probability_tables:
            card_types |= probability_table.keys()
        return card_types

    def to_packwars_dict(self):
        return [p.to_packwars_dict() for p in self.probability_tables]

class Card:
    def __init__(self, name, rarity, layout, mana_cost):
        self.name = name
        self.rarity = rarity
        self.layout = layout
        self.mana_cost = mana_cost

    @classmethod
    def from_mtgjson_dict(cls, set_code, data):
        mana_cost = data.get('manaCost', None)
        return cls(
            name=data['name'],
            rarity=data['rarity'],
            layout=data['layout'],
            mana_cost=mana_cost,
        )

    def is_card_type(self, set_code, card_type):
        if card_type == 'Steamflogger Boss':
            return self.name == 'Steamflogger Boss'
        elif card_type == 'double faced common':
            return self.layout == "double-faced" and not self.mana_cost and self.rarity == 'Common'
        elif card_type == 'double faced uncommon':
            return self.layout == "double-faced" and not self.mana_cost and self.rarity == 'Uncommon'
        elif card_type == 'double faced rare':
            return self.layout == "double-faced" and not self.mana_cost and self.rarity == 'Rare'
        elif card_type == 'double faced mythic rare':
            return self.layout == "double-faced" and not self.mana_cost and self.rarity == 'Mythic Rare'
        elif card_type == 'double faced':
            return self.layout == "double-faced" and not self.mana_cost
        else:
            return card_type == self.rarity.lower()
        # if set_code in ('TSB', 'TSP') and rarity == 'Special':
            # return True
        # elif rarity == 'Basic Land':
            # return "land"
        # elif layout == "double-faced" and mana_cost:
            # return "double faced"
        # return rarity.lower()

    @classmethod
    def make_card_type(cls, set_code, rarity, layout, mana_cost):
        """
        Given a set code, and a card json dump, try to figure out which value
        in the booster listing it matches. E.g., Timeshift has, under booster,
        "timeshifted purple", which means you need a card from timeshift with
        the "special" rarity.

        This method should return "timeshifted purple" for a card with those
        properties.

        >>> Card.make_card_type('TSP', 'special', 'normal', '{1}{W}')
        'timeshifted purple'
        >>> Card.make_card_type('ABC', 'common', 'normal', '{2}{U}')
        'common'
        """
        if set_code in ('TSB', 'TSP') and rarity == 'Special':
            return "timeshifted purple"
        elif rarity == 'Basic Land':
            return "land"
        elif layout == "double-faced" and mana_cost:
            return "double faced"
        return rarity.lower()

class Set:
    SET_TYPE_EXPANSION = 'expansion'
    SET_TYPE_CORE = 'core'
    SET_TYPE_JOKE = 'un'

    class UnknownSetTypeError(Exception):
        pass

    def __init__(self, name, code, release_date, set_type, block, booster_format, cards):
        self.name = name
        self.code = code
        self.release_date = release_date
        self.set_type = set_type
        self.block = block
        self.booster_format = booster_format
        self.cards = cards

    @classmethod
    def from_mtgjson_dict(cls, data):
        release_date = datetime.datetime.strptime(data['releaseDate'], "%Y-%m-%d"),
        set_type = cls.set_type_from_string(data['type'])
        booster_format = BoosterFormat.from_mtgjson_dict(data['booster'])
        cards = [Card.from_mtgjson_dict(data['code'], card_data) for card_data in data['cards']]
        return cls(
            name=data['name'],
            code=data['code'],
            release_date=release_date,
            set_type=set_type,
            block=data.get('block', None),
            booster_format=booster_format,
            cards=cards,
        )

    @classmethod
    def set_type_from_string(cls, set_type_string):
        if set_type_string == 'expansion':
            return cls.SET_TYPE_EXPANSION
        elif set_type_string == 'core':
            return cls.SET_TYPE_CORE
        elif set_type_string == 'un':
            return cls.SET_TYPE_JOKE
        else:
            raise cls.UnknownSetTypeError(set_type_string)

    def to_packwars_dict(self):
        cards_by_type = {}
        for card_type in self.booster_format.required_card_types():
            cards_by_type[card_type] = list(set([card.name for card in self.cards if card.is_card_type(self.code, card_type)]))
            if not cards_by_type[card_type] and card_type == 'land':
                cards_by_type[card_type] = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
            assert cards_by_type[card_type], "Set {} requires {} for its booster but none are found {!r}".format(self.code, card_type, self.booster_format.required_card_types())
        return {
            "name": self.make_name(self.block, self.name),
            "boosterFormat": self.booster_format.to_packwars_dict(),
            "cardsByType": cards_by_type,
        }

    @classmethod
    def make_name(cls, block, name):
        """
        >>> Set.make_name("Shadowmoor", "Eventide")
        'Shadowmoor - Eventide'
        >>> Set.make_name("Shards of Alara", "Shards of Alara")
        'Shards of Alara'
        """
        if not block or block == name: 
            return name
        return "{block} - {name}".format(block=block, name=name)


class AllSets:
    """
    expected output I think:
    [
        {
            "name": "Lorwyn",
            "booster": {
                "common": 10,
                "uncommon: 5,
                "rare": 1
            },
            "rare": ["A", "B"],
            "uncommon": ["X", "Y"],
        }
    ]

    new output:
    [
        {
            "name": "Lorwyn",
            "boosterFormat": [
                {"common": 1.0},
                {"common": 1.0},
                {"common": 1.0},
                {"uncommon": 1.0},
                {"uncommon": 1.0},
                {"rare": 0.8, "mythic": 0.2}
            ],
            "cardsByType": {
                "rare": ["A", "B"],
                "uncommon": ["X", "Y"],
            }
        }
    ]
    """
    def __init__(self, sets):
        self.sets = sets
        self.sets.sort(key=lambda s: s.release_date)

    @classmethod
    def from_mtgjson_file(cls, mtgjson_file):
        sets = []
        # parse json file from mtgjson to dict
        set_data_by_code = hack_mtgjson_dict(json.load(mtgjson_file))
        # for each set in the dict, turn it into a Set object
        for code, set_data in set_data_by_code.items():
            try:
                sets.append(Set.from_mtgjson_dict(set_data))
            except Set.UnknownSetTypeError as e:
                pass
                #sys.stderr.write("skipping set: {}\n".format(code))
        return cls(sets=sets)

    def to_packwars_dict(self):
        return [s.to_packwars_dict() for s in self.sets]

    def dump_packwars_jsonp(self, outfile, json_only):
        if not json_only:
            outfile.write("mtgJSON(")
        json.dump(self.to_packwars_dict(), outfile)
        if not json_only:
            outfile.write(")")

def hack_mtgjson_dict(data):
    """
    Fix broken crap in mtgjson file
    """
    # move all cards from TSB into TSP and delete TSB
    # data['TSP']['cards'].extend(data['TSB']['cards'])
    # del data['TSB']

    # No timespiral
    del data['TSB']
    del data['TSP']
    del data['PLC']
    del data['FUT']

    return data

if __name__ == "__main__":
    import argparse
    import sys
    import json
    parser = argparse.ArgumentParser(description="Convert mtgjson file to packwars jsonp file")
    parser.add_argument("-t", "--test", action="store_true", help="run tests")
    parser.add_argument("-j", "--json", action="store_true", help="generate as json instead of jsonp")
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

    args = parser.parse_args()
    if args.test:
        import doctest
        doctest.testmod()
        sys.exit()

    all_sets = AllSets.from_mtgjson_file(args.infile)
    all_sets.dump_packwars_jsonp(args.outfile, args.json)
