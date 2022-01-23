from app import app
from flask import render_template, request
from app.forms import GachaForm
import numpy as np
import bisect


@app.route('/', methods=['GET', 'POST'])
def my_form_post():
    if request.method == "GET":
        return render_template("index.html", pity=0, guarantee="1", acquaint=0, primo=0)
    if request.form["primo"] == "":
        primo = 0
    else:
        primo = int(request.form["primo"])
    if request.form['acquaint'] == "":
        acquaint = 0
    else:
        acquaint = int(request.form['acquaint'])
    wishes = primo // 160 + acquaint
    test = request.form["guarantee"]
    g = True if test == "2" else False
    pity = 0 if request.form["pity"]=="" else int(request.form["pity"])
    results = []
    for i in range(7):
        results.append(deterministic(i, wishes, g, pity))
    return render_template("results.html", temp=wishes, pity=pity, guarantee=test, acquaint=acquaint, primo=primo,
                           results=results)


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
        return 1
    return f"{100*fullPDF.cumsum()[wishes]:.2f}"


def bin_search(value, array):
    return bisect.bisect_left(array, value)




