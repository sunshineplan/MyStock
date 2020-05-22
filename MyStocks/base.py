#!/usr/bin/env python3

from datetime import date, datetime, time, timedelta

from aiohttp import ClientTimeout, request


async def fetch(url, **kwargs):
    async with request('GET', url, timeout=ClientTimeout(total=2), **kwargs) as response:
        assert response.status == 200
        return await response.json()


class SSE:
    def __init__(self, code=None):
        self.code = code
        self.pattern = r'000[0-1]\d{2}|(51[0-358]|60[0-3]|688)\d{3}'

    async def realtime(self):
        try:
            self.snap = await fetch(
                f'http://yunhq.sse.com.cn:32041/v1/sh1/snap/{self.code}')
            self.exist = True
        except:
            self.exist = False
        if self.exist:
            self._realtime = {'index': 'SSE',
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
            return self._realtime
        return {'index': 'SSE', 'code': self.code, 'name': 'n/a'}

    async def chart(self):
        await self.realtime()
        if self.exist:
            try:
                response = await fetch(
                    f'http://yunhq.sse.com.cn:32041/v1/sh1/line/{self.code}')
                line = response['line']
            except:
                return None
            chart = []
            sessions = [(datetime.combine(date.today(), time(9, 30)) +
                         timedelta(minutes=i)).strftime('%H:%M') for i in range(331)]
            lunch = [(datetime.combine(date.today(), time(11, 31)) +
                      timedelta(minutes=i)).strftime('%H:%M') for i in range(90)]
            for i in lunch:
                sessions.remove(i)
            for l in line:
                chart.append({'x': sessions.pop(0), 'y': l[0]})
            return {'last': self._realtime['last'], 'chart': chart}
        return None


class SZSE:
    def __init__(self, code=None):
        self.code = code
        self.pattern = r'(00[0-3]|159|300|399)\d{3}'

    async def realtime(self):
        try:
            response = await fetch('http://www.szse.cn/api/market/ssjjhq/getTimeData',
                                   params={'marketId': 1, 'code': self.code})
            self.exist = True if response['code'] == '0' else False
        except:
            self.exist = False
        if self.exist:
            self.data = response['data']
        if self.exist:
            try:
                sell5 = [list(i.values())
                         for i in self.data['sellbuy5'][:5]]
                buy5 = [list(i.values())
                        for i in self.data['sellbuy5'][5:]]
            except KeyError:
                sell5 = None
                buy5 = None
            self._realtime = {'index': 'SZSE',
                             'code': self.data['code'],
                             'name': self.data['name'],
                             'now': self.data['now'],
                             'change': self.data['delta'],
                             'percent': self.data['deltaPercent']+'%',
                             'sell5': sell5,
                             'buy5': buy5,
                             'high': self.data['high'],
                             'low': self.data['low'],
                             'open': self.data['open'],
                             'last': self.data['close'],
                             'update': self.data['marketTime']}
            return self._realtime
        return {'index': 'SZSE', 'code': self.code}

    async def chart(self):
        await self.realtime()
        if self.exist:
            picupdata = self.data['picupdata']
            chart = []
            for i in picupdata:
                chart.append({'x': i[0], 'y': i[1]})
            return {'last': float(self._realtime['last']), 'chart': chart}
        return None
