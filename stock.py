from datetime import date, datetime, time, timedelta
from re import fullmatch

import requests
from flask import Blueprint, abort, g, jsonify, render_template, request

from db import get_db, init_db

bp = Blueprint('stock', __name__,)


@bp.route('/')
def index():
    return render_template('mystocks.html')


def get_stock(index, code):
    indices = ['SSE', 'SZSE']
    if index in indices:
        return eval(index+'("'+code+'")')
    else:
        return None


@bp.route('/<string:index>/<string:code>')
def chart(index, code):
    stock = get_stock(index, code)
    if stock:
        if fullmatch('(00[0-3]|159|300|399|51[0-3]|60[0-3]|688)\d{3}|51\d{4}', code):
            return render_template('chart.html', index=index, code=code)
        return render_template('chart.html', index=index, code='n/a')
    abort(404)


@bp.route('/get')
def get():
    index = request.args.get('index')
    code = request.args.get('code')
    q = request.args.get('q')
    return jsonify(eval('get_stock(index, code).'+q))


@bp.route('/mystocks')
def get_mystocks():
    db = get_db()
    try:
        if g.user:
            my_stocks = db.execute(
                'SELECT idx, code FROM stock WHERE user_id = ?', (g.user['id'],)).fetchall()
        else:
            my_stocks = db.execute(
                'SELECT idx, code FROM stock WHERE user_id = 0').fetchall()
    except:
        tables = db.execute('SELECT name FROM sqlite_master').fetchall()
        if tables == []:
            init_db()
            return get_mystocks()
    result = []
    for i in my_stocks:
        result.append(get_stock(i['idx'], i['code']).realtime)
    return jsonify(result)


@bp.route('/indices')
def get_indices():
    indices = {'沪': SSE('000001').realtime, '深': SZSE('399001').realtime,
               '创': SZSE('399006').realtime, '中小板': SZSE('399005').realtime}
    return jsonify(indices)


class SSE:
    def __init__(self, code):
        try:
            if requests.get('http://yunhq.sse.com.cn:32041/v1/sh1/snap/%s' % code, timeout=1).status_code == 200:
                self.exist = True
            else:
                self.exist = False
        except:
            self.exist = False
        if self.exist:
            try:
                self.snap = requests.get(
                    'http://yunhq.sse.com.cn:32041/v1/sh1/snap/%s' % code, timeout=1).json()
                self.line = requests.get(
                    'http://yunhq.sse.com.cn:32041/v1/sh1/line/%s' % code, timeout=1).json()
            except:
                self.exist = False

    @property
    def realtime(self):
        if self.exist:
            realtime = {'index': 'SSE',
                        'code': self.snap['code'],
                        'name': self.snap['snap'][0].strip(),
                        'now': self.snap['snap'][5],
                        'change': self.snap['snap'][6],
                        'percent': str(self.snap['snap'][7])+'%',
                        'sell5': [[self.snap['snap'][-1][i], self.snap['snap'][-1][i+1]] for i in range(0, 10, 2)],
                        'buy5': [[self.snap['snap'][-2][i], self.snap['snap'][-2][i+1]] for i in range(0, 10, 2)],
                        'high': self.snap['snap'][3],
                        'low': self.snap['snap'][4],
                        'open': self.snap['snap'][2],
                        'last': self.snap['snap'][1],
                        'update': str(self.snap['date'])+'.'+str(self.snap['time'])}
            return realtime
        return None

    @property
    def chart(self):
        if self.exist:
            line = self.line['line']
            chart = []
            sessions = [(datetime.combine(date.today(), time(9, 30)) +
                         timedelta(minutes=i)).strftime('%H:%M') for i in range(331)]
            lunch = [(datetime.combine(date.today(), time(11, 31)) +
                      timedelta(minutes=i)).strftime('%H:%M') for i in range(90)]
            for i in lunch:
                sessions.remove(i)
            for l in line:
                chart.append({'x': sessions.pop(0), 'y': l[0]})
            return {'last': self.realtime['last'], 'chart': chart}
        return None


class SZSE:
    def __init__(self, code):
        try:
            self.json = requests.get(
                'http://www.szse.cn/api/market/ssjjhq/getTimeData', params={'marketId': 1, 'code': code}, timeout=1).json()
            self.exist = True if self.json['code'] == '0' else False
        except:
            self.exist = False

    @property
    def realtime(self):
        if self.exist:
            try:
                sell5 = [list(i.values()) for i in self.json['data']['sellbuy5'][:5]]
                buy5 = [list(i.values()) for i in self.json['data']['sellbuy5'][5:]]
            except KeyError:
                sell5 = None
                buy5 = None
            realtime = {'index': 'SZSE',
                        'code': self.json['data']['code'],
                        'name': self.json['data']['name'],
                        'now': self.json['data']['now'],
                        'change': self.json['data']['delta'],
                        'percent': self.json['data']['deltaPercent']+'%',
                        'sell5': sell5,
                        'buy5': buy5,
                        'high': self.json['data']['high'],
                        'low': self.json['data']['low'],
                        'open': self.json['data']['open'],
                        'last': self.json['data']['close'],
                        'update': self.json['data']['marketTime']}
            return realtime
        return None

    @property
    def chart(self):
        if self.exist:
            picupdata = self.json['data']['picupdata']
            chart = []
            for i in picupdata:
                chart.append({'x': i[0], 'y': i[1]})
            return {'last': float(self.realtime['last']), 'chart': chart}
        return None
