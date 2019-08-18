from flask import Flask, abort, jsonify, render_template, request

from stock import SSE, SZSE

app = Flask(__name__)


def get_stock(index, code):
    indices = ['SSE', 'SZSE']
    if index in indices:
        return eval(index+'("'+code+'")')
    else:
        return None


@app.route('/<string:index>/<string:code>')
def chart(index, code):
    stock = get_stock(index, code)
    if stock:
        if stock.exist:
            return render_template('chart.html', index=index, code=code)
    abort(404)


@app.route('/get')
def get():
    index = request.args.get('index')
    code = request.args.get('code')
    q = request.args.get('q')
    return jsonify(eval('get_stock(index, code).'+q))


if __name__ == '__main__':
    app.run(port=80, debug=True)
