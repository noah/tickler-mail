#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# todo-tickle.py - script to output a list of pending ticklers.
# I run it in ~/.zshrc for a subtle reminder of daily todos
#
# (c) 2014, Noah K. Tilton <code@tilton.co>, GPL

import textwrap

from glob import glob

from termcolor import colored

from utils import tickle_iterator

# TODO:
# add INBOX folder, but only for messages with X-Tickler:yes

TICKLE_PATH = glob("/home/noah*/mail/noah*@*.com/@todo")[0]
INDENT      = ' ' * 4
LINE_LEN    = 102

tickles = sorted([T for T in tickle_iterator(TICKLE_PATH) ], key=lambda
                 x: x['due_in'])
for T in tickles:

    msg = T['src'][T['key']]
    print colored(('-' * LINE_LEN), 'magenta')
    if T['due_in'] is not None:
        if T['due']:
            print colored('%s ago' % T['due_in'], 'red'),
        else:
            print colored('due in %s' % T['due_in'], 'green'),
    print colored('/%s' % T['boxname'], 'cyan'),
    print colored(' '.join(msg['subject'].splitlines()), 'white', attrs=['bold']),
    print colored(msg['from'], 'blue')
    msgtext = msg.get_payload(decode=True)
    if msgtext is None: msgtext = ''
    msgtext = ' '.join(msgtext.splitlines()).strip()
    if len(msgtext) < 1: msgtext = '~~~'
    abbr = '\n'.join(textwrap.wrap(msgtext[:96], LINE_LEN, initial_indent=INDENT, subsequent_indent=INDENT))
    print (colored(abbr, 'yellow'))
