import datetime
import io
import os
import weightdb

from flask import Flask, render_template, request, jsonify, make_response

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

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

@app.route('/weight/plot/all')
@app.route('/weight/plot/<int:days>')
def weight_plot(days=None):
    db = weightdb.WeightDb(DBNAME)
    hist = db.get_weights(days)

    d = []
    w = []
    for h in hist:
        dstr = h[0]
        if '.' in dstr:
            idot = dstr.index('.')
            dstr = dstr[:idot]
        d.append(datetime.datetime.strptime(dstr, '%Y-%m-%d %H:%M:%S'))
        w.append(h[1])

    #fig = Figure(figsize=(2,1.5))
    fig = Figure()
    ax = fig.add_subplot(111)

    ax.plot_date(d, w, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    fig.autofmt_xdate()

    canvas = FigureCanvas(fig)
    png_output = io.StringIO()
    canvas.print_png(png_output)

    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'

    return response

if __name__ == '__main__':
    app.run()

