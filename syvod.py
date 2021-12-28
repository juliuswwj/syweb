#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio, socket

EOM=b'<>'
EOMLN=b'<>\x0a'


def log(msg):
    print('[syvod]', msg)

status = None
sock = None
playlist = []
localChanged = False
async def run():
    global status, playlist, sock, localChanged
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    myip = s.getsockname()[0]
    s.close()

    log('myip='+myip)
    while True:
        status = None
        sock = None
        try:
            r, w = await asyncio.open_connection(myip, 7888)
        except ConnectionError as e:
            log(str(e))
            await asyncio.sleep(5)
            continue

        log('connected')

        sock = w
        while not r.at_eof():
            try:
                msg = str((await r.readuntil(EOM))[:-2], 'utf-8')
            except asyncio.IncompleteReadError as e:
                break
            except ConnectionError as e:
                break

            #print('<', msg)
            
            # echo
            if msg[0] == '~':
                w.write(bytes(';' + msg[1:], 'utf-8') + EOMLN)
                continue

            # status
            if msg[0] == '?':
                status = msg[2:].split(',')
                continue

            # current play list
            if msg[0] == '$':
                ts = msg[2:].split('||')
                playlist = []
                for n in range(len(ts)//5):
                    playlist.append(int(ts[n*5]))
                continue

            if msg[0] == 'A': localChanged = True

async def call(msg):
    global sock
    if not sock: return
    #print('>', msg)
    sock.write(bytes(msg, 'utf-8') + EOMLN)
    await sock.drain()

if __name__ == '__main__':
    asyncio.run(run())
