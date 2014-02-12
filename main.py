#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# tickler-mail - maildir-based email follow-up reminders (aka ticklers,
# boomerangs, etc)
#
# (c) 2014, Noah K. Tilton <code@tilton.co>, GPL

from datetime import datetime
from time import mktime
from os import walk, stat
from os.path import basename, dirname, join
from glob import glob
from email import message_from_file
from shutil import move as mv

import parsedatetime as pdt
cal = pdt.Calendar()

from gi.repository import Notify


class PARSE_TYPES:
    # https://bear.im/code/parsedatetime/docs/parsedatetime.parsedatetime-pysrc.html#Calendar.parse
    FAIL        = 0
    DATE        = 1
    TIME        = 2
    DATETIME    = 3


class DateTimeParseException(Exception): pass


def parse_time(nl_time, start_time=None):
    """ De-suck parsedatetime.Calendar.parse """
    parse_date, PARSE_STATUS = cal.parse( nl_time, sourceTime=start_time)
    if PARSE_STATUS is PARSE_TYPES.FAIL:
        raise DateTimeParseException("Couldn't parse relative datetime", nl_time)
    elif PARSE_STATUS > PARSE_TYPES.FAIL:
        parse_date = datetime.fromtimestamp(mktime(parse_date))
    else:
        raise DateTimeParseException("Unknown PARSE_TYPE", PARSE_STATUS)
    return parse_date


def notify(message):
    Notify.init("mail reminder")
    if message.is_multipart():
        msg = "%s attachments ..." % len(message.get_payload())
    else:
        msg = "%s ..." % message.get_payload(decode=True)[:100]
        try:
            n = Notify.Notification.new("\n".join(["=== reminder ===",message.get("from",
                                        ""), message.get("subject", "")]),
                                        msg, "dialog-information")
            n.set_timeout(0)
            n.set_urgency(Notify.Urgency.CRITICAL)
            n.show()
        except Exception as e:
            print(e)

if __name__ == '__main__':

    thetime     = datetime.now()
    TICKLE_PATH = glob("/home/noah*/mail/noah*@*.com/@todo")[0]
    INBOX       = glob("/home/noah*/mail/noah*@*.com/INBOX/cur")[0]

    for root, subdirs, files in walk( TICKLE_PATH, topdown=True ):
        # remove maildir meta directories from top-level
        if root == TICKLE_PATH:
            subdirs.remove('cur')
            subdirs.remove('tmp')
            subdirs.remove('new')
        else:
            for file in files:
                nl_time         = basename( dirname( root ) ).replace('-', ' ')
                ctime           = datetime.fromtimestamp(stat(join(root, file)).st_ctime)
                remind_time     = parse_time(nl_time, start_time=ctime)

                #   \/ tickle check \/
                FILE_REALPATH = join(root, file)
                if thetime <= remind_time:
                    message = None
                    with open(FILE_REALPATH, 'r') as fp:
                        message = message_from_file(fp)
                        message.add_header("X-Tickler", "yes")
                        notify( message )
                    with open(FILE_REALPATH, 'w') as fp:
                        fp.write( unicode( message ) )
                    mv(FILE_REALPATH, INBOX)
                    print FILE_REALPATH, "->", INBOX
