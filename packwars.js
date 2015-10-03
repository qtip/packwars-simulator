var LANDS = ["Plains", "Island", "Swamp", "Mountain", "Forest"];

var PackWarsSimulator = function(sets) {
    this.sets = sets;
}

PackWarsSimulator.prototype.makeDeck = function(packs) {
    var cards = Array.prototype.concat.apply([], packs);
    for (i = 0; i < packs.length; i++) {
        cards = cards.concat(LANDS, LANDS);
    }
    cards.sort();

    var out = [];
    var current = null;
    var idx = 0;
    for (i = 0; i < cards.length; i++) {
        if(cards[i] != current) {
            // new card!
            if (current != null) {
                out.push(i-idx + " " + current);
            }
            current = cards[i];
            idx = i;
        }
    }
    if (current != null) {
        out.push(i-idx + " " + current);
    }

    return out.join("\n");
}

var takeOne = function(array) {
    return array[Math.floor(Math.random()*array.length)];
}

PackWarsSimulator.prototype.makePack = function(setIdx) {
    var set = this.sets[setIdx];
    var pack = [];
    for (i = 0; i < 10; i++) {
        pack.push(takeOne(set.commons));
    }
    for (i = 0; i < 3; i++) {
        pack.push(takeOne(set.uncommons));
    }
    if (set.mythics.length == 0 || Math.random() > 1/8) {
        pack.push(takeOne(set.rares));
    } else {
        pack.push(takeOne(set.mythics));
    }
    pack.push(takeOne(LANDS));
    return pack;

}

PackWarsSimulator.prototype.setNames = function() {
    var out = [];
    for (i = 0; i < this.sets.length; i++) {
        out.push({"key": "" + i, "name": this.sets[i].name});
    }
    return out;
}
