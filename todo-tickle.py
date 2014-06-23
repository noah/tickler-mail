#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# todo-tickle.py - script to output a list of pending ticklers.
# I run it in ~/.zshrc for a subtle reminder of daily todos
#
# (c) 2014, Noah K. Tilton <code@tilton.co>, GPL

from glob import glob

from termcolor import colored

from utils import tickle_iterator

# TODO:
# add INBOX folder, but only for messages with X-Tickler:yes

TICKLE_PATH = glob("/home/noah*/mail/noah*@*.com/@todo")[0]

for date, boxname, msg in sorted( [ (T['due_in'], T['boxname'], T['src'][T['key']],)
                                    for T in tickle_iterator( TICKLE_PATH ) ],
                                key=lambda x: x[0]):
        print ('-' * 82)
        print (colored(date, 'green')),
        print (boxname),
        print (colored(msg['subject'], 'red')),
        print (colored(msg['from'], 'blue'))
        try:
            abbr = msg.get_payload(decode=True)[:200].rstrip()
        except:
            abbr = ''
        msg = "%s ..." % abbr
        print (colored(msg, 'yellow'))
