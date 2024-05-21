function dataenc(e,ktimes) {
    for (var t = ktimes % 10, i = (0 == t && (t = 1),
    []), a = 0; a < e.length; a++) {
        var n = e.charCodeAt(a) ^ t;
        i.push(String.fromCharCode(n))
    }
    return i.join("")
}