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
import logging
import sys
import status

class StatusDatabase(object):

    _DB_NAME = 'sickbeard_status.db'

    def __init__(self):
        self.path = deluge.common.get_default_config_dir(self._DB_NAME)

        # Usure why these alias to ask are required, but after a while of running
        # without these lines the pickler throws exceptions about no module named
        # 'status'.
        sys.modules['sickbeard.status'] = status
        sys.modules['status']           = status

        # Enable write-back to prevent high(er) CPU usage
        self.d        = shelve.open(self.path, writeback=True)

        self.log      = logging.getLogger('deluge.sickbeard.statusdb.StatusDatabase')
        self.log.info("Opened status database '%s'", self.path)

        # Initialze status objects
        for torrent_id in self.d:
            self.d[torrent_id].initialize()
        self.sync()

    def __del__(self):
        if hasattr(self, 'd'):
            self.d.close()
            self.log.info("Closed status database '%s'", self.path)

    def __iter__(self):
        return self.d.__iter__()

    def __getitem__(self, key):
        return self.d.__getitem__(key)

    def next(self):
        return self.d.next()

    def iteritems(self):
        return self.d.iteritems()

    def itervalues(self):
        return self.d.itervalues()

    def sync(self):
        return self.d.sync()

    def update(self, status):

        tid     = status.torrent_id

        key         = str(tid)
        self.d[key] = status

        # write status/cache to disk (write-back is true)
        self.d.sync()

        return True

    def delete(self, torrent_id, sync = True):
        key = torrent_id

        try:
            d = self.d

            d[key].finalize()

            del d[key]

            if sync:
                self.d.sync()
        except Exception as e:
            self.log.error("Failed to delete status object for torrent %s from status db" % (key))
            #for line in error.format_exception():
            #    self.log.error("%s" % line)
            return False
        else:
            return True

if __name__ == "__main__":
    pass
    # note: use status_dump.py for further debugging
