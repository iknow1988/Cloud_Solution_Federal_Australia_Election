# -*- coding: utf-8 -*-
"""
Created on Thu May  9 03:44:49 2019

@author: Lenovo
"""
import couchdb
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from collections import Counter

app = Flask(__name__)

cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})




state = {
 'new south wales': 1,
 'victoria': 2,
 'queensland': 3,
 'south australia': 4,
 'western australia': 5, 
 'tasmania': 6, 
 'northern territory': 7,
 'australian capital territory': 8
}


user = "admin"
password = "p01ss0n"
couch_server = couchdb.Server("http://%s:%s@103.6.254.96:9584/" % (user, password))
db = couch_server['tweeter_test']


@app.route("/initial/", methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def hello():
    view = db.view('_design/counts/_view/location_state', reduce=True, group=True)
    count = Counter()

    for item in view:
        if item.key:
            key = item.key
            count[key] += item.value
    result = {}
    for key in state.keys():
        result[key] = count[key]

    return jsonify(result)

@app.route("/state/", methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def state_total_count():
    view = db.view('_design/counts/_view/location_state', reduce=True, group=True)
    count = Counter()

    for item in view:
        if item.key:
            key = item.key
            count[key] += item.value
    result = {}
    for key in state.keys():
        result[state[key]] = count[key]

    return jsonify(result)


if __name__ == '__main__':
    app.run()