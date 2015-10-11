# packwars-simulator
Packwars (aka Mini-Master) Simulator

This simulator takes one or more sets as input, randomly generates boosters for those sets,
adds an appropriate amount of lands, then builds a .dec file.

# Install
```sh
wget mtgjson.com/json/AllSets.json.zip
unzip AllSets.json.zip
./convert.py < AllSets.json > AllSets.jsonp
```

Serve via HTTP.

# Live Version

http://packwars.mrdanielsnider.com
