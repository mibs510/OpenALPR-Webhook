#  Copyright (c) 2023. Connor McMillan
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#  following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#
#
#
#
#

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
