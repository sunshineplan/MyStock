from re import fullmatch

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
        if fullmatch('(00[0-3]|159|300|51[0-3]|60[0-3]|688)\d{3}|51\d{4}', code):
            return render_template('chart.html', index=index, code=code)
        return render_template('chart.html', index=index, code='n/a')
    abort(404)


@app.route('/get')
def get():
    index = request.args.get('index')
    code = request.args.get('code')
    q = request.args.get('q')
    return jsonify(eval('get_stock(index, code).'+q))


if __name__ == '__main__':
    app.run(port=80, debug=True)
