# Deluge Sickbeard plugin

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import logging
import sys
import os

from abc     import ABCMeta, abstractmethod
from logging import *
from logging import currentframe

# Exact copy from logging module
if hasattr(sys, 'frozen'): #support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)


class SickbeardLogger(Logger):
    """
    Custom Logger reporting correct filename, lineno etc information
    when using logging wrapper functions/classes. Due to an extra call, the
    default Logger is not able to correctly identify the calling stackframe,
    causing wrong filenames and linenumbers to be logged.

    note: all wrapper functions/classes should be included in this module,
          otherwise the wrong filename and lineno will stil be reported.
    """

    def __init__(self, name):
        super(SickbeardLogger, self).__init__(name)

    # Excact same as Logger.findCaller, but now using this module's _srcfile
    # to locate how many stackframes should be reversed.
    def findCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv

class DispatchingFormatter(object):
    """
    Format messages differently based on LogRecord content. Order of
    supplied dispatch formatters is important. The first disptach
    formatter reporting that it finds itself suitable to format the
    message will be used to format the message.
    """

    def __init__(self, formatters):
        self._formatters = formatters

    def format(self, record):
        for formatter in self._formatters:
            if formatter.dispatch(record):
                break
        return formatter.format(record)

class DispatchFormatter(logging.Formatter):
    """
    Base class for a dispatch formatter. Formatter must implement the
    dispatch() method. Based on content available in the LogRecord, the
    dispatcher may decided it is suitable to format the contant.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def dispatch(self, record):
        return

class DefaultFormatter(DispatchFormatter):
    """Format any message."""

    def __init__(self):
        super(DefaultFormatter, self).__init__('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')

    def dispatch(self, record):
        return True

class TaskFormatter(DispatchFormatter):
    """Format message if task information is available"""

    def __init__(self):
        super(TaskFormatter, self).__init__('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - worker %(task-worker-id)d, task %(task-worker-seq)s: %(message)s')

    def dispatch(self, record):
        if hasattr(record, 'task'):
            return True

class TaskLoggerAdapter(logging.LoggerAdapter):
    """
    Logger Adapter allowing to log task information. Tightly coupled with the
    TaskFormatter which is the formatter being able to format task information
    logged by this adapter.

    Usage: task   = Task()
           logger = getLogger('test')
           alog   = TaskLoggerAdapter(logger)
           alog.info(task, 'New task created')
    """

    def __init__(self, logger, extra = {}):
        super(TaskLoggerAdapter, self).__init__(logger, extra)
        self.task = None

    def set_task(self, task):
        self.task = task

    def _get_extra(self, task):
        if task:
            return {
                "task"           : task,
                "task-worker-id" : task.worker_id,
                "task-worker-seq": task.worker_seq
            }
        else:
            raise Exception("No task data assigned.")

    def info(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        kwargs['extra'].update(self._get_extra(self.task))
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        kwargs['extra'].update(self._get_extra(self.task))
        self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        kwargs['extra'].update(self._get_extra(self.task))
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        kwargs['extra'].update(self._get_extra(self.task))
        self.logger.warning(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        kwargs['extra'].update(self._get_extra(self.task))
        self.logger.exception(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        kwargs['extra'].update(self._get_extra(self.task))
        self.logger.critical(msg, *args, **kwargs)

class TaskHandler(logging.Handler):
    """Cache task related logging in task"""

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        if hasattr(record, 'task'):
            #record.task.output.append(self.format(record))
            record.task.output.append(record)

def getLogger(name):
    """
    Get logger based on custom logger class. Restores original logger class
    to prevent intrusion on other parts of the application which expect the
    default logger class.
    """

    current = logging.getLoggerClass()
    logging.setLoggerClass(SickbeardLogger)
    logger = logging.getLogger(name)
    logging.setLoggerClass(current)

    return logger

if __name__ == "__main__":

    pass # see log_test.py for tests
