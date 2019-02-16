from flask import Flask, render_template, flash, request
from process import Process
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
#secret key is needed to keep the client-side sessions secure
app.config["SECRET_KEY"] = "d4e71ce128cf06fdd41a908fdf5cc2e2"

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    dropdown_list = []
    try:
        countryField = pd.read_csv("AVOXI Coding Challenge - Automation - ITFS Packages.csv")
        process = Process(countryField)
        dropdown_list = set(i for i in countryField.Country)
    except Exception as e:
        return render_template('home.html', dropdown_list=sorted(dropdown_list), data=e, valType="")

    #Handle the posting of the data
    if request.method == 'POST':
        country = str(request.form['country'])
        data = process.processData(country)
        if isinstance(data, list):
            valType = "list"
        else:
            valType = ""
        return render_template('home.html', dropdown_list=sorted(dropdown_list), data=data, valType=valType)

    return render_template('home.html', dropdown_list=sorted(dropdown_list), data=[])


if __name__ == "__main__":
    app.run(debug=True)
