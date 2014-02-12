# Description 

A script implementing "[tickler
file](http://en.wikipedia.org/wiki/Tickler_file)" or "boomerang"-style
reminders.

Intended to be used in conjunction with Mutt or another command line MUA.

The basic idea relies on the following convention:

Messages are saved to a Maildir hierarchy, such as:

    todo/
        tomorrow
        in-three-days
        next-week
        next-month
        next-year

Where the name of the inner directory, with dashes ('-') removed, is a
human-readable string that can be parsed by the
[parsedatetime](https://github.com/bear/parsedatetime) module.

The script simply walks this todo directory and for each directory and
email within that directory, it compares the timestamp of the file to
the current date + the delta of the *evaluation of the directory name*.

The todo directory is defined in the code by the constant `TICKLE_PATH`.

# Example

* If on Monday I save an email X to the "in-three-days" folder, then the
algorithm when called in the future will compare the current time to the
`ctime(3)` of the email + the time delta of
`parsedatetime.Calendar.parse("in three days")`.

* If the time now exceeds the save time + delta, then it triggers
notifications.

Notifications, for my purposes, include:

1. Firing a notify-send message; and
2. Add an `X-Tickler` header
3. Moving the email back to the inbox (the "boomerang" event)

# Protip

Adding this to `muttrc` highlights messages that have been triggered and are currently "tickling":

    color index white red '~h "X-Tickler:.*yes"'  


With any luck, I'll never forget to do anything important ever again.
