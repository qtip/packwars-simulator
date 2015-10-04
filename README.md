# packwars-simulator
Packwars (aka Mini-Master) Simulator

This simulator builds packs with ten commons, three uncommons, and one rare (or mythic rare ⅛ of the time). Obviously, this isn't precise for all sets, but it's good enough for playing.

# Install
```sh
wget mtgjson.com/json/AllSets.json.zip
unzip AllSets.json.zip
./convert.py < AllSets.json > AllSets.jsonp
```

Serve via HTTP.

# Live Version

http://packwars.mrdanielsnider.com
