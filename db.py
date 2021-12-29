#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, pyodbc, shutil

CACHE='cache\\'
def connectMDB(mdb):
    return pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' % mdb)

def QueryVOD(table, filter=None):
    omdb = '..\\song.mdb'
    mdb = CACHE + 'song.mdb'
    try:
        ost = os.stat(omdb)
        st = os.stat(mdb)
        copying = ost.st_mtime > st.st_mtime+1
    except:
        copying = True
    if copying: shutil.copy(omdb, mdb)

    conn = connectMDB(mdb)
    cursor = conn.cursor()
    sql = 'SELECT * FROM VOD_' + table
    if filter: sql += ' WHERE ' + filter
    cursor.execute(sql)

    columns = [column[0] for column in cursor.description]

    rows = []
    for row in cursor.fetchall():
        rows.append(row)

    conn.close()
    return columns, rows

def QueryDataList(table):
    cols, rows = QueryVOD(table)
    return [row[1] for row in rows]

PLACES = ['大陆', '香港', '台湾', '海外']
SEXES = ['男', '女', '乐队']
LANGS = QueryDataList('Lang')
TYPES = QueryDataList('AudioType')

colSingers, rowSingers = QueryVOD('singer')
# SingerName -> ID
SINGER_NAMES = {}
for r in rowSingers:
    SINGER_NAMES[r[1]] = r[0]
idxSingerName = colSingers.index('SingerName')
idxPlace = colSingers.index('Place')
idxSex = colSingers.index('Sex')
idxSingerImg = colSingers.index('SingerImg')
idxSpell = colSingers.index('Spell')
idxClickCount = colSingers.index('ClickCount')

def QuerySong():
    mdb = CACHE + 'skysong.mdb'
    if not os.path.exists(mdb):
        shutil.copy('..\\skysong.mdb', mdb)
    conn = connectMDB(mdb)

    cursor = conn.cursor()
    cursor.execute('SELECT SongID,SONGNAME,SINGER,SongLANG,SongTYPE,spell,DownLoadCount FROM Net_song')

    columns = [column[0] for column in cursor.description]

    rows = []
    for row in cursor.fetchall():
        rows.append(list(row))

    conn.close()
    return columns, rows

colSongs, rowSongs = QuerySong()
idxSongID = colSongs.index('SongID')
idxSONGNAME = colSongs.index('SONGNAME')
idxSINGER = colSongs.index('SINGER')
idxSongLANG = colSongs.index('SongLANG')
idxSongTYPE = colSongs.index('SongTYPE')
idxspell = colSongs.index('spell')
idxDownLoadCount = colSongs.index('DownLoadCount')
idxLocalID = 0
idxFileName = 0

def UpdateLocal():
    global colSongs, rowSongs, idxSINGER, idxSONGNAME, idxSongLANG, idxLocalID, idxFileName

    # extend    
    if idxLocalID == 0:
        idxLocalID = len(colSongs)
        idxFileName = idxLocalID+1
        colSongs.extend(['LocalID', 'FileName'])
        for row in rowSongs: row.extend([0, ''])

    # make {SINGER-SONGNAME-SongLANG -> idx}
    sidx = {}
    for n, row in enumerate(rowSongs):
        k = '%s-%s-%s' % (row[idxSINGER], row[idxSONGNAME], row[idxSongLANG])
        if k in sidx:
            sidx[k].add(n)
        else:
            sidx[k] = set((n,))

    cols, rows = QueryVOD('song')
    iSONGNAME = cols.index('SONGNAME')
    iSINGER = cols.index('SINGER')
    iSongID = cols.index('SongID')
    iSongLANG = cols.index('SongLANG')
    iFileName = cols.index('FileName')

    for row in rows:
        k = '%s-%s-%s' % (row[iSINGER], row[iSONGNAME], row[iSongLANG])
        nset = sidx.get(k, None)
        if not nset: continue
        for n in nset:
            rowSongs[n][idxLocalID] = row[iSongID]
            rowSongs[n][idxFileName] = row[iFileName]
            #print(k, rowSongs[n][0], rowSongs[n][ext:])

UpdateLocal()

def place(r):
    global idxPlace
    try:
        return PLACES[int(r[idxPlace])]
    except:
        return 'N/A'

def lang(r):
    global idxSongLANG
    try:
        return LANGS[int(r[idxSongLANG])]
    except:
        return 'N/A'

def type(r):
    global idxSongTYPE
    try:
        return TYPES[int(r[idxSongTYPE])]
    except:
        return 'N/A'

def spanRun(key, id, param=None):
    arglist = '\'%s\'' % id
    if param: arglist += ',\'%s\'' % param
    return '<span onclick="run%s(%s)">[<font color=blue>%s</font>]</span> ' % (key, arglist, key)

def SongTable(filter):
    global idxSONGNAME, idxSongID, idxLocalID, idxSongLANG, idxSongTYPE, idxSINGER, idxDownLoadCount, rowSongs

    rows = []
    for r in rowSongs:
        if filter(r): rows.append(r)
        if len(rows) >= 1500: break
    if len(rows) == 0: return ''
    rows.sort(key=lambda r: -r[idxDownLoadCount])

    table = '<table class="sortable">\n<tr><th></th><th>名称</th><th>歌手</th><th>语言</th><th>类型</th><th>热度</th></tr>\n'

    for r in rows:
        table += '<tr><td>'
        if r[idxLocalID] > 0:
            table += spanRun('Q', r[idxLocalID], r[idxSONGNAME])
        else:
            table += spanRun('D', r[idxSongID], r[idxSONGNAME])
        table += '</td>'

        ss = []
        for s in r[idxSINGER].split('_'):
            if s in SINGER_NAMES:
                ss.append('<a href=/?q=.S%d>%s</a>' % (SINGER_NAMES[s], s))
            else:
                ss.append(s)

        table += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (r[idxSONGNAME], ' '.join(ss), lang(r), type(r), r[idxDownLoadCount])
        table += '</tr>\n'

    table += '</table><br><font size=-1>共<font color=green>%d</font>首</font>\n' % len(rows)
    return table

def PlayTable(playlist):
    global idxSONGNAME, idxSongID, idxLocalID, idxSongLANG, idxSongTYPE, idxSINGER, rowSongs

    songs = {}
    for r in rowSongs:
        if r[idxLocalID] in playlist: songs[r[idxLocalID]] = r
        if r[idxSongID] in playlist: songs[r[idxSongID]] = r

    table = '<table class="sortable">\n<tr><th></th><th>名称</th><th>歌手</th><th>语言</th><th>类型</th></tr>\n'

    for n, id in enumerate(playlist):
        if id not in songs: continue

        table += '<tr><td>'
        if n > 1: table += spanRun('T', n)
        if n > 0: table += spanRun('X', n)
        table += '</td>'

        r = songs[id]
        table += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (r[idxSONGNAME], r[idxSINGER], lang(r), type(r))
        table += '</tr>\n'

    table += '</table>\n'
    return table

lastSinger = None
def SingerTable(filter):
    global colSingers, rowSingers, idxSingerName, idxPlace, idxSex, idxClickCount, lastSinger

    lastSinger = None

    rows = []
    for r in rowSingers:
        if filter(r): rows.append(r)
        if len(rows) >= 300: break
    if len(rows) == 0: return ''
    rows.sort(key=lambda r: -r[idxClickCount])

    if len(rows) == 1:
        r = rows[0]
        lastSinger = r[idxSingerName]
        table = '<table width=100%%>\n<tr><td width=50%%><img  width=100%% src=/image/%s /></td><td>%s<br>%s<br>%s</td></tr></table>\n' % (r[0], lastSinger, place(r), r[idxSex])

    else:
        table = '<table class="sortable">\n<tr><th>歌手</th><th>地区</th><th>性别</th></tr>\n'
        for r in rows:
            table += '<tr><td><a href=/?q=.S%s>%s</a></td><td>%s</td><td>%s</td></tr>\n' % (r[0], r[idxSingerName], place(r), r[idxSex])
        table += '</table>\n'
    return table

