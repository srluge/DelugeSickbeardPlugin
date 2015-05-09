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
import log
from   log     import DispatchingFormatter, \
                      TaskFormatter, \
                      DefaultFormatter, \
                      TaskHandler, \
                      TaskLoggerAdapter

if __name__ == "__main__":

    logger  = log.getLogger('main')
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(DispatchingFormatter([ TaskFormatter(), DefaultFormatter() ]))
    logger.addHandler(handler)

    handler = TaskHandler()
    handler.setFormatter(TaskFormatter())
    logger.addHandler(handler)

    logger.error('Sickbeard Logger test')

    class Task():
        def __init__(self):
            self.output = []
            self.worker = 1
            self.seq    = 10

    def test_logger():
        logger = log.getLogger('main.test')
        adapter = TaskLoggerAdapter(logger)
        t = Task()
        adapter.set_task(t)
        adapter.info('hi')
        adapter.info('test2')
        print t.output

    test_logger()

