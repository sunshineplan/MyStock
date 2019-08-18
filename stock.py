from datetime import date, datetime, time, timedelta

import requests


class SSE:
    def __init__(self, code):
        if requests.get('http://yunhq.sse.com.cn:32041/v1/sh1/snap/%s' % code).status_code == 200:
            self.exist = True
        else:
            self.exist = False
        if self.exist:
            self.snap = requests.get(
                'http://yunhq.sse.com.cn:32041/v1/sh1/snap/%s' % code).json()
            self.line = requests.get(
                'http://yunhq.sse.com.cn:32041/v1/sh1/line/%s' % code).json()

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
        self.json = requests.get(
            'http://www.szse.cn/api/market/ssjjhq/getTimeData', params={'marketId': 1, 'code': code}).json()
        self.exist = True if self.json['code'] == '0' else False

    @property
    def realtime(self):
        if self.exist:
            realtime = {'index': 'SZSE',
                        'code': self.json['data']['code'],
                        'name': self.json['data']['name'],
                        'now': self.json['data']['now'],
                        'change': self.json['data']['delta'],
                        'percent': self.json['data']['deltaPercent']+'%',
                        'sell5': [list(i.values()) for i in self.json['data']['sellbuy5'][:5]],
                        'buy5': [list(i.values()) for i in self.json['data']['sellbuy5'][5:]],
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
