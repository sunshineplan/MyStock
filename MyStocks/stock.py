#!/usr/bin/env python3

import asyncio
from json import loads
from re import fullmatch

import requests
from flask import Blueprint, g, jsonify, render_template, request

from MyStocks.base import SSE, SZSE
from MyStocks.db import get_db, init_db

bp = Blueprint('stock', __name__)

INDICES = ['SSE', 'SZSE']


def get_stock(index, code):
    if index in INDICES:
        return eval(index+'("'+code+'")')
    else:
        return None


async def get_realtime(stock):
    def get_stock_realtime(stock):
        stock = get_stock(stock['idx'], stock['code'])
        return stock.realtime()
    if isinstance(stock, list):
        return await asyncio.gather(*[get_stock_realtime(s) for s in stock])
    else:
        return await get_stock_realtime(stock)


async def get_chart(stock):
    stock = get_stock(stock['idx'], stock['code'])
    return await stock.chart()


@bp.route('/')
def index():
    return render_template('mystocks.html')


@bp.route('/<string:index>/<string:code>')
def chart(index, code):
    if index in INDICES:
        if fullmatch(eval(index+'().pattern'), code):
            return render_template('chart.html', index=index, code=code)
    return render_template('chart.html', index='n/a', code='n/a')


@bp.route('/get')
def get():
    index = request.args.get('index')
    code = request.args.get('code')
    q = request.args.get('q')
    if q == 'realtime':
        return jsonify(asyncio.run(get_realtime({'idx': index, 'code': code})))
    elif q == 'chart':
        return jsonify(asyncio.run(get_chart({'idx': index, 'code': code})))
    else:
        return ''


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
    return jsonify(asyncio.run(get_realtime(my_stocks)))


@bp.route('/indices')
def get_indices():
    indices = [{'idx': 'SSE', 'code': '000001'}, {'idx': 'SZSE', 'code': '399001'},
               {'idx': 'SZSE', 'code': '399006'}, {'idx': 'SZSE', 'code': '399005'}]
    realtimes = asyncio.run(get_realtime(indices))
    return jsonify({'沪': realtimes[0], '深': realtimes[1],
                    '创': realtimes[2], '中小板': realtimes[3]})


@bp.route('/suggest')
def get_suggest():
    keyword = request.args.get('keyword')
    sse = 'http://query.sse.com.cn/search/getPrepareSearchResult.do'
    szse = 'http://www.szse.cn/api/search/suggest'
    try:
        headers = {'Referer': 'http://www.sse.com.cn/'}
        sse_suggest = requests.get(sse, params={'searchword': '%'+keyword+'%', 'search': 'ycxjs'},
                                   headers=headers, timeout=1).json()['data']
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
