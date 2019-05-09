# -*- coding: utf-8 -*-
"""
Created on Thu May  9 03:44:49 2019

@author: Lenovo
"""

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)

cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})

@app.route("/", methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def hello():
    response = jsonify({'count': 10})
    return response

if __name__ == '__main__':
    app.run()