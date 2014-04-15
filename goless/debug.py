DEBUG = False


def debug(s, *args):
    if DEBUG:
        print s % args
