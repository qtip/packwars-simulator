
var PackWarsSimulator = function(sets) {
    this.sets = sets;
}

PackWarsSimulator.LANDS = ["Plains", "Island", "Swamp", "Mountain", "Forest"];

PackWarsSimulator.arrayToDec = function(array) {
    array.sort();

    var out = [];
    var current = null;
    var idx = 0;
    var i;
    for (i = 0; i < array.length; i++) {
        if(array[i] != current) {
            // new card!
            if (current != null) {
                out.push(i-idx + " " + current);
            }
            current = array[i];
            idx = i;
        }
    }
    if (current != null) {
        out.push(i-idx + " " + current);
    }

    return out.join("\n");
}

PackWarsSimulator.landsForCards = function(cardCount) {
    out = []
    var amount;
    if (cardCount == 15) {
        amount = 3;
    } else {
        amount = Math.ceil(cardCount*2/15);
    }
    var i;
    for (i = 0; i < amount; i++) {
        out = out.concat(PackWarsSimulator.LANDS);
    }
    return out;
}

PackWarsSimulator.prototype.makeDeck = function(idxs) {
    var cards = [];
    var i;
    for (i = 0; i < idxs.length; i++) {
        cards = cards.concat(this.makeBooster(idxs[i]));
    }
    cards = cards.concat(PackWarsSimulator.landsForCards(cards.length));
    return PackWarsSimulator.arrayToDec(cards);
}

PackWarsSimulator.sample = function(array, n) {
    out = [];
    var i;
    for (i = 0; i < n; i++) {
        var idx = Math.floor(Math.random() * (array.length-i)) + i;
        var tmp = array[idx];
        array[idx] = array[i];
        array[i] = tmp;
        out.push(tmp);
    }
    return out;
}

PackWarsSimulator.prototype.makeBoosterCountThing = function(setIdx) {
    /*
     * Go from [{"common": 1.0}, {"common": 1.0}]
     * To {"common": 2}
     * That is, take a booster format and choose cards from each then
     * count how many of each card type was chosen
     */
    var boosterFormat = this.sets[setIdx].boosterFormat;
    var i;
    var out = {};
    for (i = 0; i < boosterFormat.length; i++) {
        var probability_table = boosterFormat[i];
        // pick from probability table
        var u = Math.random();
        var sum = 0.0;
        for (key in probability_table) {
            sum += probability_table[key];
            if (u <= sum) {
                out[key] = (out[key] || 0) + 1;
                break;
            }
        }
    }
    return out;
}

PackWarsSimulator.prototype.makeBooster = function(setIdx) {
    var sample = PackWarsSimulator.sample;
    var set = this.sets[setIdx];
    var booster = [];
    var boosterCountThing = this.makeBoosterCountThing(setIdx);
    console.log(boosterCountThing);
    for (kind in boosterCountThing) {
        var count = boosterCountThing[kind];
        console.log(kind, count)
        booster = booster.concat(sample(set.cardsByType[kind], count));
    }
    console.log(booster);
    return booster;
}

PackWarsSimulator.prototype.setNames = function() {
    var out = [];
    var i;
    for (i = 0; i < this.sets.length; i++) {
        out.push({"key": "" + i, "name": this.sets[i].name});
    }
    return out;
}
