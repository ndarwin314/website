from app import app
from flask import render_template, request, redirect, url_for
from app.forms import GachaForm
from flask_restful import Resource, Api
import numpy as np
import bisect


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def initial():
    return render_template("index.html")


@app.route("/character", methods=["GET", "POST"])
def character():
    if request.method == "GET":
        if request.args:
            args = request.args
            wishes = int(args["primo"]+args["crystal"]) // 160 + int(args["fate"])
            pity = int(args["pity"])
            g = True if args['guarantee'] == 'True' else False
            results = deterministic2(wishes, g, pity)
            return render_template("character.html",
                                   pity=pity,
                                   guarantee=args['guarantee'],
                                   fate=args["fate"],
                                   primo=args['primo'],
                                   crystal=args['crystal'],
                                   results=results)
        return render_template("character.html", pity=0, guarantee="1", fate=0, primo=0, crystal=0)
    elif request.method == 'POST':
        # TODO: this is horrible
        if request.form["primo"] == "":
            primo = 0
        else:
            primo = int(request.form["primo"])
        if request.form['fate'] == "":
            fate = 0
        else:
            fate = int(request.form['fate'])

        if request.form['crystal'] == "":
            crystal = 0
        else:
            crystal = int(request.form['crystal'])
        test = request.form["guarantee"]
        g = True if test == "True" else False
        pity = 0 if request.form["pity"] == "" else int(request.form["pity"])
        wishes = int((primo + crystal) // 160 + fate)
        results = deterministic2(wishes, g, pity)
        return render_template('character.html', pity=pity, guarantee=g, primo=primo, fate=fate, crystal=crystal, results=results)

# TODO reusing this much code is definitely poor design but idgaf rn
@app.route("/weapon", methods=["GET", "POST"])
def weapon():
    if request.method == "GET":
        if request.args:
            args = request.args
            wishes = int(args["primo"]+args["crystal"]) // 160 + int(args["fate"])
            pity = int(args["pity"])
            g = True if args['guarantee'] == 'True' else False
            results = deterministic2(wishes, g, pity)
            return render_template("weapon.html",
                                   pity=pity,
                                   guarantee=args['guarantee'],
                                   fate=args["fate"],
                                   primo=args['primo'],
                                   crystal=args['crystal'],
                                   results=results)
        return render_template("weapon.html", pity=0, guarantee="1", fate=0, primo=0, crystal=0)
    elif request.method == 'POST':
        # TODO: this is horrible
        if request.form["primo"] == "":
            primo = 0
        else:
            primo = int(request.form["primo"])
        if request.form['fate'] == "":
            fate = 0
        else:
            fate = int(request.form['fate'])

        if request.form['crystal'] == "":
            crystal = 0
        else:
            crystal = int(request.form['crystal'])
        test = request.form["guarantee"]
        g = True if test == "True" else False
        pity = 0 if request.form["pity"] == "" else int(request.form["pity"])
        wishes = int((primo + crystal) // 160 + fate)
        results = weaponCalc(wishes, g, pity)
        return render_template('weapon.html', pity=pity, guarantee=g, primo=primo, fate=fate, crystal=crystal, results=results)


"""@app.route("/webservice")
def webservice():
    return deterministic2()"""


def deterministic(constellations=0, wishes=0, guarantee=False, pity=0):
    rampRate = 0.06
    P = 0.006
    cons = constellations
    base = np.zeros((91,))
    base[0] = 0
    base[1:74] = P
    base[90] = 1
    for i in range(74, 90):
        base[i] = P + rampRate * (i - 73)
    ones = np.ones((91,))
    temp = ones - base
    basePDF = np.zeros((91,))
    for i in range(91):
        basePDF[i] = np.prod(temp[0:i]) * base[i]
    doublePDF = np.zeros((181,))
    doublePDF[0:91] += basePDF
    for i in range(1, 90):
        doublePDF[i:i + 91] += basePDF[i] * basePDF
    doublePDF /= 2
    pityPDF = np.zeros((91 - pity,))
    fullPDF = np.zeros((181 - pity - 90 * guarantee,))
    pityPDF[0] = 0
    for i in range(1, 91 - pity):
        pityPDF[i] = np.prod(temp[pity + 1:i + pity]) * base[i + pity]
    fullPDF[0:91 - pity] = pityPDF
    if not guarantee:
        for i in range(1, 90 - pity):
            fullPDF[i:i + 91] += pityPDF[i] * basePDF
        fullPDF /= 2

    # fullPDF = basePDF if guarantee else doublePDF
    for i in range(cons):
        fullPDF = np.convolve(fullPDF, doublePDF)
    if wishes >= len(fullPDF) - 1:
        return 100
    return f"{100*fullPDF.cumsum()[wishes]:.2f}"


def cumulative(array, index):
    if index >= array.size:
        return 100
    return f"{100*array.cumsum()[index]:.2f}"

def weaponCalc(wishes=0, guarantee=True, pity=0):
    base = np.zeros((81,))
    p = 0.007
    ramp = 0.06 #temporary
    base[0] = 0
    base[1:63] = p
    base[80] = 1
    for i in range(63, 80):
        base[i] = min(1, p + ramp * (i-62))
    ones = np.ones((81,))
    oneMinus = ones - base
    basePDF = np.zeros((81,))
    for i in range(81):
        basePDF[i] = np.prod(oneMinus[0:i]) * base[i]
    doublePDF = np.convolve(basePDF, basePDF)
    triplePDF = np.convolve(doublePDF, basePDF)
    fullPDF = 23 / 64 * triplePDF
    fullPDF[0:81] += 3/8*basePDF
    fullPDF[0:161] += 17/64*doublePDF
    pityPDF = np.zeros((81,))
    pityPDF[0] = 0
    initialPDF = np.zeros((241-pity,))
    for i in range(1, 81 - pity):
        pityPDF[i] = np.prod(oneMinus[pity + 1:i + pity]) * base[i + pity]
    if guarantee:
        initialPDF[0:81-pity] += 1 / 2 * pityPDF
        temp = np.convolve(pityPDF, basePDF)
        initialPDF[0:161 - pity] += 3 / 16 * temp
        temp = np.convolve(temp, basePDF)
        initialPDF += 5 / 16 * temp
    else:
        initialPDF[0:81-pity] += 3 / 8 * pityPDF
        temp = np.convolve(pityPDF, basePDF)
        initialPDF[0:161-pity] += 17 / 64 * temp
        temp = np.convolve(temp, basePDF)
        initialPDF += 23 / 64 * temp
    probabilities = [cumulative(initialPDF, wishes)]
    fullPDF = initialPDF
    for i in range(4):
        fullPDF = np.convolve(fullPDF, triplePDF)
        probabilities.append(cumulative(fullPDF, wishes))
    return probabilities








def deterministic2(wishes=0, guarantee=False, pity=0):
    rampRate = 0.06
    P = 0.006
    cons = 6
    probabilities = []
    base = np.zeros((91,))
    base[0] = 0
    base[1:74] = P
    base[90] = 1
    for i in range(74, 90):
        base[i] = P + rampRate * (i - 73)
    ones = np.ones((91,))
    temp = ones - base
    basePDF = np.zeros((91,))
    for i in range(91):
        basePDF[i] = np.prod(temp[0:i]) * base[i]
    doublePDF = np.zeros((181,))
    doublePDF[0:91] += basePDF
    for i in range(1, 90):
        doublePDF[i:i + 91] += basePDF[i] * basePDF
    doublePDF /= 2
    pityPDF = np.zeros((91 - pity,))
    fullPDF = np.zeros((181 - pity - 90 * guarantee,))
    pityPDF[0] = 0
    for i in range(1, 91 - pity):
        pityPDF[i] = np.prod(temp[pity + 1:i + pity]) * base[i + pity]
    fullPDF[0:91 - pity] = pityPDF
    if not guarantee:
        for i in range(1, 90 - pity):
            fullPDF[i:i + 91] += pityPDF[i] * basePDF
        fullPDF /= 2
    probabilities.append(cumulative(fullPDF, wishes))
    # fullPDF = basePDF if guarantee else doublePDF
    for i in range(cons):
        fullPDF = np.convolve(fullPDF, doublePDF)
        probabilities.append(cumulative(fullPDF, wishes))
    return probabilities


def bin_search(value, array):
    return bisect.bisect_left(array, value)




