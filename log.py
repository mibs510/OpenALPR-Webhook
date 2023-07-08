import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import click

logdir = os.path.abspath(os.path.dirname(__file__)) + '/logs'


def init(filename: str):
    class RemoveColorFilter(logging.Filter):
        def filter(self, record):
            if record and record.msg and isinstance(record.msg, str):
                record.msg = click.unstyle(record.msg)
            return True

    if not os.path.exists(logdir):
        os.makedirs(logdir)
    logging.getLogger()
    logging.getLogger().setLevel(logging.DEBUG)

    """ Catch all unhandled exceptions """
    # sys.excepthook = exception_hook

    """ .log File Handler """
    dot_log_file_handler = RotatingFileHandler(logdir + "/" + filename, maxBytes=10000000, backupCount=9)
    dot_log_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)s %(message)s", datefmt="[%m/%d/%y %I:%M %p]")
    dot_log_file_handler.setFormatter(dot_log_formatter)
    logging.getLogger().addHandler(dot_log_file_handler)

    """ stdout/stderr - Redis Rq Workers """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)s %(message)s",
                                  datefmt="[%m/%d/%y %I:%M %p]")

    dot_log_file_handler.addFilter(RemoveColorFilter())
    dot_log_file_handler.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)


def exception_hook(type, value, traceback):
    logging.exception("Unhandled exception raised outside of try/except!\n\tType: {}\n\tValue: {}\n\tTraceback: {}".
                      format(type, value, traceback), exc_info=sys.exc_info())
