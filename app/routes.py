from app import app
from flask import render_template, request, redirect, url_for
from app.forms import GachaForm
from flask_restful import Resource, Api
import numpy as np
import bisect


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def initial():
    if request.method == "GET":
        if request.args:
            args = request.args
            results = []
            wishes = int(args["primos"]) // 160 + int(args["fates"])
            pity = int(args["pity"])
            g = True if args['guarantee'] == 'True' else False
            for i in range(7):
                results.append(deterministic(i, wishes, g, pity))
            return render_template("results.html",
                                   pity=pity,
                                   guarantee=args['guarantee'],
                                   fate=args["fates"],
                                   primo=args['primos'],
                                   results=results)
        return render_template("index.html", pity=0, guarantee="1", acquaint=0, primo=0)
    elif request.method == 'POST':
        if request.form["primo"] == "":
            primo = 0
        else:
            primo = int(request.form["primo"])
        if request.form['fate'] == "":
            fates = 0
        else:
            fates = int(request.form['fate'])
        test = request.form["guarantee"]
        g = True if test == "True" else False
        pity = 0 if request.form["pity"] == "" else int(request.form["pity"])
        return redirect(url_for('initial', pity=pity, guarantee=g, primos=primo, fates=fates))


"""@app.route("/webservice")
def webservice():
    return deterministic2()"""


rampRate = 0.06
P = 0.006

def deterministic(constellations=0, wishes=0, guarantee=False, pity=0):
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

def cumulative(array,index):
    if index > array.size:
        return 1
    return array.cumsum()[index]

def deterministic2(wishes=0, guarantee=False, pity=0):
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
    print(probabilities)
    return {i: probabilities[i] for i in range(7)}


def bin_search(value, array):
    return bisect.bisect_left(array, value)




