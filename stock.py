from datetime import date, datetime, time, timedelta
from json import loads
from re import fullmatch

import requests
from flask import Blueprint, g, jsonify, render_template, request

from db import get_db, init_db

bp = Blueprint('stock', __name__)


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
    if index == 'SSE':
        if fullmatch(SSE().pattern, code):
            return render_template('chart.html', index=index, code=code)
    elif index == 'SZSE':
        if fullmatch(SZSE().pattern, code):
            return render_template('chart.html', index=index, code=code)
    return render_template('chart.html', index=index, code='n/a')


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
                'SELECT idx, code FROM stock WHERE user_id = ? ORDER BY seq', (g.user['id'],)).fetchall()
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


@bp.route('/suggest')
def get_suggest():
    keyword = request.args.get('keyword')
    sse = 'http://query.sse.com.cn/search/getPrepareSearchResult.do'
    szse = 'http://www.szse.cn/api/search/suggest'
    try:
        sse_suggest = requests.get(sse, params={'searchword': '%'+keyword+'%', 'search': 'ycxjs'}, headers={
                                   'Referer': 'http://www.sse.com.cn/'}, timeout=1).json()['data']
    except:
        sse_suggest = []
    try:
        szse_suggest = requests.post(
            szse, params={'keyword': keyword}, timeout=1).json()
    except:
        szse_suggest = []
    suggest = []
    for i in sse_suggest:
        code = i['CODE']
        if fullmatch(SSE().pattern, code):
            suggest.append({'category': 'SSE', 'code': code,
                            'name': i['WORD'], 'type': i['CATEGORY']})
    for i in szse_suggest:
        code = i['wordB'].replace(
            '<span class="keyword">', '').replace('</span>', '')
        if fullmatch(SZSE().pattern, code):
            suggest.append({'category': 'SZSE', 'code': code,
                            'name': i['value'], 'type': i['type']})
    return jsonify(suggest)


@bp.route('/star', methods=('GET', 'POST'))
def star():
    refer = request.referrer
    index = refer.split('/')[-2]
    code = refer.split('/')[-1]
    db = get_db()
    if request.method == 'GET':
        if g.user:
            stock = db.execute(
                'SELECT * FROM stock WHERE idx = ? AND code = ? AND user_id = ?', (index, code, g.user['id'])).fetchone()
            if stock:
                return 'True'
        return 'False'
    action = request.form.get('action')
    if g.user:
        if action == 'unstar':
            db.execute('DELETE FROM stock WHERE idx = ? AND code = ? AND user_id = ?',
                       (index, code, g.user['id']))
            db.commit()
        else:
            db.execute('INSERT INTO stock (idx, code, user_id) VALUES (?, ?, ?)',
                       (index, code, g.user['id']))
            db.commit()
        return '1'
    return '0'


@bp.route('/reorder', methods=('POST',))
def reorder():
    orig = loads(request.form.get('orig'))
    dest = loads(request.form.get('dest'))
    db = get_db()
    if g.user:
        orig_seq = db.execute(
            'SELECT seq FROM stock WHERE idx = ? AND code = ? AND user_id = ?', (orig[0], orig[1], g.user['id'])).fetchone()['seq']
        if dest != 'top':
            dest_seq = db.execute(
                'SELECT seq FROM stock WHERE idx = ? AND code = ? AND user_id = ?', (dest[0], dest[1], g.user['id'])).fetchone()['seq']
        else:
            dest_seq = 0
        if orig_seq > dest_seq:
            dest_seq += 1
            db.execute('UPDATE stock SET seq = seq + 1 WHERE seq >= ? AND user_id = ? AND seq < ?',
                       (dest_seq, g.user['id'], orig_seq))
        else:
            db.execute('UPDATE stock SET seq = seq - 1 WHERE seq <= ? AND user_id = ? AND seq > ?',
                       (dest_seq, g.user['id'], orig_seq))
        db.execute('UPDATE stock SET seq = ? WHERE idx = ? AND code = ? AND user_id = ?',
                   (dest_seq, orig[0], orig[1], g.user['id']))
        db.commit()
        return '1'
    return '0'


class SSE:
    def __init__(self, code=None):
        self.code = code
        self.pattern = '000[0-1]\d{2}|(51[0-358]|60[0-3]|688)\d{3}'
        try:
            if requests.get(f'http://yunhq.sse.com.cn:32041/v1/sh1/snap/{code}', timeout=1).status_code == 200:
                self.exist = True
            else:
                self.exist = False
        except:
            self.exist = False
        if self.exist:
            try:
                self.snap = requests.get(
                    f'http://yunhq.sse.com.cn:32041/v1/sh1/snap/{code}', timeout=1).json()
                self.line = requests.get(
                    f'http://yunhq.sse.com.cn:32041/v1/sh1/line/{code}', timeout=1).json()
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
        return {'index': 'SSE', 'code': self.code, 'name': 'n/a'}

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
    def __init__(self, code=None):
        self.code = code
        self.pattern = '(00[0-3]|159|300|399)\d{3}'
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
                sell5 = [list(i.values())
                         for i in self.json['data']['sellbuy5'][:5]]
                buy5 = [list(i.values())
                        for i in self.json['data']['sellbuy5'][5:]]
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
        return {'index': 'SZSE', 'code': self.code}

    @property
    def chart(self):
        if self.exist:
            picupdata = self.json['data']['picupdata']
            chart = []
            for i in picupdata:
                chart.append({'x': i[0], 'y': i[1]})
            return {'last': float(self.realtime['last']), 'chart': chart}
        return None
