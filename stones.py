import datetime
import io
import os
import weightdb

from flask import Flask, render_template, request, jsonify, make_response

app = Flask(__name__)
app.debug = True

DBNAME = os.path.join(app.root_path, 'db', 'weight.db')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weight/add')
def weight_add():
    weight = request.args.get('weight')
    when = request.args.get('when')

    try:
        when = datetime.datetime.strptime(when, '%m/%d/%Y %I:%M %p')

        db = weightdb.WeightDb(DBNAME)
        db.add_weight(weight, when)

    except Exception as e:
        return jsonify({'status':False})

    return jsonify({'status':True})

@app.route('/weight/get/all')
@app.route('/weight/get/<int:days>')
def weight_get(days=None):
    db = weightdb.WeightDb(DBNAME)
    wh = weightdb.WeightHistory(db, days)
    return jsonify(wh.dict_all())

if __name__ == '__main__':
    app.run()

