#!/usr/bin/env python
import os
import sys
import signal

CURDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(CURDIR, 'helpers'))

from client import client, prompt, end_of_block

log = None
# uncomment the line below for debugging
#log=sys.stdout

with client(name='client1>', log=log) as client1, client(name='client2>', log=log) as client2:
    client1.expect(prompt)
    client2.expect(prompt)

    client1.send('DROP TABLE IF EXISTS test.lv')
    client1.expect(prompt)
    client1.send('DROP TABLE IF EXISTS test.mt')
    client1.expect(prompt)
    client1.send('SET temporary_live_view_timeout=1')
    client1.expect(prompt)
    client1.send('CREATE TABLE test.mt (a Int32) Engine=MergeTree order by tuple()')
    client1.expect(prompt)
    client1.send('CREATE TEMPORARY LIVE VIEW test.lv AS SELECT sum(a) FROM test.mt')
    client1.expect(prompt)
    client1.send('WATCH test.lv')
    client1.expect(r'0.*1' + end_of_block)
    client2.send('INSERT INTO test.mt VALUES (1),(2),(3)')
    client2.expect(prompt)
    client1.expect(r'6.*2' + end_of_block)
    client2.send('INSERT INTO test.mt VALUES (4),(5),(6)')
    client2.expect(prompt)
    client1.expect(r'21.*3' + end_of_block)
    # send Ctrl-C
    os.kill(client1.process.pid, signal.SIGINT)
    client1.expect(prompt)
    client1.send('SELECT sleep(1)')
    client1.expect(prompt)
    client1.send('DROP TABLE test.lv')
    client1.expect('Table test.lv doesn\'t exist')
    client1.expect(prompt)
    client1.send('DROP TABLE test.mt')
    client1.expect(prompt)
