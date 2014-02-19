from os import walk, stat
from time import mktime
from datetime import datetime, timedelta
from mailbox import Maildir
from os.path import basename, dirname
from email.errors import MessageParseError

from gi.repository import Notify
import parsedatetime as pdt
cal = pdt.Calendar()


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


def tickle_iterator( path ):

    thetime = datetime.now()
    for box, subdirs, _ in walk( path, topdown=True ):
        # remove maildir meta directories from top-level
        subdirs.remove('cur')
        subdirs.remove('tmp')
        subdirs.remove('new')
        src_mbox = Maildir(box, factory=None)
        src_mbox.lock()
        for key in src_mbox.iterkeys():
            try:
                path        = '/'.join([box, src_mbox._toc[key]])
                tickle_time = parse_time(basename( box ).replace('-', ' '), start_time=datetime.fromtimestamp(stat(path).st_ctime))
                due_in      = thetime - tickle_time
                yield {
                        'src'       : src_mbox,
                        'key'       : key,
                        'boxname'   : basename( box ),
                        'path'      : path,
                        'due_in'    : due_in,
                        'due'       : due_in > timedelta(seconds=1),
                }
            except MessageParseError:
                continue # malformed msg, ignore
        src_mbox.flush()
        src_mbox.unlock()


def maildirname(maildir):
    return basename(dirname(maildir._paths["new"]))


def mv(src, dst, msg, key):
    print("mv %s/%s -> %s" % (maildirname(src), msg.get("subject", ''), maildirname(dst)))
    dst.lock()
    dst.add(msg)
    dst.flush()
    dst.unlock()
    src.lock()
    src.discard(key)
    src.flush()
    src.unlock()
