#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# tickler-mail - maildir-based email follow-up reminders (aka ticklers,
# boomerangs, etc)
#
# (c) 2014, Noah K. Tilton <code@tilton.co>, GPL

from glob import glob

from mailbox import Maildir
from utils import notify, tickle_iterator, mv

if __name__ == '__main__':

    INBOX       = glob("/home/noah*/mail/noah*@*.com/INBOX")[0]
    TICKLE_PATH = glob("/home/noah*/mail/noah*@*.com/@todo")[0]

    for T in tickle_iterator( TICKLE_PATH ):
        if T['due']:
            # mark as tickling
            msg = T['src'][T['key']]
            del msg['X-Tickler']
            msg['X-Tickler'] = 'yes'
            # mark read
            msg.add_flag('S')
            # notify
            notify( msg )
            # move message to inbox
            mv(T['src'], Maildir(INBOX), msg, T['key'])
