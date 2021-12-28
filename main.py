#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install aiohttp pyodbc

from aiohttp import web
import asyncio, logging, random, os
import db, syvod

async def httpIndex(req):
    def go(x):
        return "<li onclick=\"go('%s')\">%s</li>" % (x[0], x[1])

    mlist = {'.local':'本地', '.top':'热门'}
    for n,v in enumerate(db.LANGS): mlist['.l%d' % n] = v
    mlist = '\n'.join(map(go, mlist.items()))
    mlist = bytes(mlist, 'utf-8')

    slist = {}
    for pn,pv in enumerate(db.PLACES):
        for sn,sv in enumerate(db.SEXES):
            if len(sv) == 1: sv += "星"
            slist['.s%d%d' % (pn, sn)] = pv + sv
    slist = '\n'.join(map(go, slist.items()))
    slist = bytes(slist, 'utf-8')

    with open("index.html", 'rb') as f:
        body = f.read().replace(b'<!--MLIST-->', mlist).replace(b'<!--SLIST-->', slist)
        return web.Response(body=body, headers={
            'Content-Type': "text/html",
        })

async def httpImage(req):
    id = int(req.match_info.get('id', '0'))
    rows = list(filter(lambda r: r[0] == id, db.rowSingers))
    if len(rows) != 1: return web.HTTPNotFound()

    jpg = "..\\Singer\\" + rows[0][db.idxSingerImg]
    with open(jpg, 'rb') as f:
        return web.Response(body=f.read(), headers={
            'Content-Type': "image/jpeg",
        })

def isalpha(s):
    for c in s:
        i = ord(c)
        if i<65 or (i>90 and i<97) or i>122: return False
    return True

async def httpContent(req):
    q = req.match_info.get('q', '.local')
    body = ''
    songFilter = None
    singerFilter = None
    if q == '.local':
        songFilter = lambda r: r[db.idxLocalID] > 0

    elif q == '.list':
        body = db.PlayTable(syvod.playlist)

    elif q == '.top':
        songFilter = lambda r: r[db.idxDownLoadCount] > 300
    
    elif q.startswith('.l'):
        songFilter = lambda r: r[db.idxSongLANG] == q[2]

    elif q.startswith('.s'):
        singerFilter = lambda r: str(r[db.idxPlace]) == q[2] and r[db.idxSex] == db.SEXES[int(q[3])]

    elif q.startswith('.S'):
        singerFilter = lambda r: r[0] == int(q[2:])

    elif q[0] == '.':
        body = 'unknown keyword ' + q

    elif isalpha(q):
        q = q.upper()
        singerFilter = lambda r: q in r[db.idxSpell]
        songFilter = lambda r: q in r[db.idxspell]
    
    else:
        singerFilter = lambda r: q in r[db.idxSingerName]
        songFilter = lambda r: q in r[db.idxSONGNAME]
    
    if singerFilter:
        body += db.SingerTable(singerFilter)
        if db.lastSinger: songFilter = lambda r: db.lastSinger in r[db.idxSINGER]

    if songFilter:
        body += db.SongTable(songFilter)

    return web.Response(body=bytes(body, 'utf-8'), headers={
            'Content-Type': "text/html",
        })


async def httpCall(req):
    data = await req.text()
    if len(data) == 0: return web.HTTPBadRequest()
    await syvod.call(data)
    return web.Response(body=bytes('OK', 'utf-8'))


async def autoplay():
    random.seed()
    while True:
        if syvod.localChanged:
            syvod.localChanged = False
            db.UpdateLocal()

        await asyncio.sleep(1)
        if syvod.playlist: continue
        await asyncio.sleep(1)
        if syvod.playlist: continue

        local = []
        for row in db.rowSongs:
            if row[db.idxLocalID] > 0: local.append(row[db.idxLocalID])

        await syvod.call('*,' + str(random.choice(local)))

async def init():
    asyncio.create_task(syvod.run())
    asyncio.create_task(autoplay())

    app = web.Application()
    logging.basicConfig(level=logging.DEBUG)
    app.add_routes([
        web.get('/', httpIndex),
        web.get('/image/{id}', httpImage),
        web.get('/content/{q}', httpContent),
        web.post('/call', httpCall),
    ])
    return app

if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))
    web.run_app(init(), port=80)
