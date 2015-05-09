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

import shelve
import deluge.common
import task
import logging
import time
import sys

from   torrent     import TorrentInfo
from   statuscache import *

class Tasklog(object):

    _DB_NAME = 'sickbeard.db'

    def __init__(self):
        self.log  = logging.getLogger('deluge.sickbeard.tasklog.Tasklog')
        self.path = deluge.common.get_default_config_dir(self._DB_NAME)

        # Usure why these alias to ask are required, but after a while of running
        # without these lines the pickler throws exceptions about no module named
        # 'task'.
        sys.modules['sickbeard.task'] = task
        sys.modules['task']           = task

        # Enable write-back to prevent CPU usage of 100%
        self.d = shelve.open(self.path, writeback=True)
        self.log.info("Opened task log '%s'", self.path)

        # Initialize status field cache
        sort = sorted(self.d.iteritems(), key=lambda x: x[1].start_time)
        self.log.info("Initializing status field cache")
        self.log.info(str(sort))
        for tupple in sort:
            task_id, tsk = tupple
            tsk.initialize()

    def __del__(self):
        if hasattr(self, 'd'):
            self.d.close()
            self.log.info("Closed task log '%s'", self.path)

        super(object, self).__init__()

    def add(self, task):

        id                  = task.id
        ts                  = task.status
        torrent             = task.torrent
        tn                  = TorrentInfo.get_display_name(torrent)
        tid                 = TorrentInfo.get_id(torrent)

        self.log.info("Saving task %s for torrent %s with status %s to task log." % (id, tn, ts))

        task.completed_time = int(time.time())

        task.persisted      = True

        key                 = str(task.id)
        self.d[key]         = task

        # write task/cache to disk (write-back it true)
        self.d.sync()

        return True

    def delete(self, task_id):
        key = str(task_id)

        try:
            d = self.d

            d[key].finalize()

            del d[key]
        except Exception as e:
            return False
        else:
            return True

    def get_all(self):
        """Return tasklog shelve dictionary"""
        return self.d

if __name__ == "__main__":
    pass
    # note: use task_dump.py for further debugging
