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

from   torrent     import *
from   log         import *
from   events      import *
from   statuscache import *

import deluge.component as component
import time

class Status(object):
    """
    Hold and check download status of a Torrent
    """
    log           = getLogger('deluge.sickbeard.status.Status')
    config        = None
    torrents      = component.get("TorrentManager").torrents
    eventmanager  = component.get("EventManager")

    def __init__(self, torrent):
        self.torrent_id    = TorrentInfo.get_id(torrent)
        self.torrent_added = TorrentInfo.get_time_added(torrent)
        self.initialize()

    def initialize(self):
        """Initialize status object"""
        self.init_field(StatusFields.DOWNLOADING         , 'downloading')
        self.init_field(StatusFields.DOWNLOAD_UNAVAILABLE, 'unavailable')
        self.init_field(StatusFields.TIME_ADDED          , 'time_added')

    def init_field(self, status_field, source_attribute):
        if not hasattr(self, "_" + source_attribute):
            # indirectly call StatusCache.update
            eval("self." + source_attribute)
        else:
            # directly call StatusCache.update
            StatusCache.update(self.torrent_id, status_field, eval("self." + source_attribute))

    def finalize(self):
        """Clean-up status object"""
        StatusCache.delete(self.torrent_id)

    def update(self):
        """Analyze torrents and update statistics"""

        if self.completed:
            return

        state             = TorrentInfo.state(self.torrent)
        name              = TorrentInfo.get_display_name(self.torrent)
        copies            = TorrentInfo.get_distributed_copies(self.torrent)
        finished          = TorrentInfo.is_finished(self.torrent)
        id                = self.torrent_id

        failed_limit      = Status.config['failed_limit']
        failed_time       = Status.config['failed_time']
        failed_interval   = Status.config['failed_interval']
        label_check       = Status.config['failed_label']
        label_check_name  = Status.config['failed_label_name']

        if self.time_added == None:
            self.time_added = self.torrent.time_added

        if label_check:
            labelplugin = component.get("CorePlugin.Label")
            if labelplugin:
                labels = labelplugin._status_get_label(id)
                if not label_check_name in labels:
                    return
            else:
                return

        if finished:
            self.failed = False
            self.process()

        if not state == "Downloading":
            return

        self.last_checked = int(time.time())

        # Assume torrent was downloaing the entire duration
        # of the previous interval.
        self.downloading  = self.downloading + failed_interval

        if copies < 1:
            # Assume torrent was unavailable the entire duration
            # of the previous interval.
            self.unavailable = self.unavailable + failed_interval

        Status.log.info("Analyzing torrent %s (d=%s/u=%d/c=%d)" % (id, self.downloading, self.unavailable, copies))

        if self.unavailable > failed_limit * 60 * 60:
            Status.log.info("Torrent (%s) un-available for longer then %d hours" % (name, failed_limit))
            self.failed = True
            self.process()
        elif self.downloading > failed_time * 60 * 60:
            Status.log.info("Torrent (%s) downloading longer then %d hours." % (name, failed_time))
            self.failed = True
            self.process()

    def process(self):
        """Post-process torrent"""
        Status.log.info("Torrent %s completed with status (%s)" % (TorrentInfo.get_display_name(self.torrent), self.failed))

        self.completed = True
        Status.eventmanager.emit(SickbeardStatusCompleted(self))

    @property
    def torrent(self):
        if self.torrent_id in Status.torrents:
            return Status.torrents[self.torrent_id]
        else:
            return None

    @property
    def torrent_id(self):
        if not hasattr(self, '_torrent_id'):
            self.torrent_id = None
        return self._torrent_id
    @torrent_id.setter
    def torrent_id(self, value):
        self._torrent_id = value

    @property
    def last_checked(self):
        if not hasattr(self, '_last_checked'):
            self.last_checked = int(time.time())     # Last time checked - seconds since 1970 (epoch)
        return self._last_checked
    @last_checked.setter
    def last_checked(self, value):
        self._last_checked = value

    @property
    def start(self):
        if not hasattr(self, '_start'):
            self.start        = int(time.time())     # Start time statistics collection - seconds since 1970 (epoch)
        return self._start
    @start.setter
    def start(self, value):
        self._start = value

    @property
    def downloading(self):
        if not hasattr(self, '_downloading'):
            self.downloading  = -1                   # Seconds torrent is being downloaded (not in paused, error, checking, etc states)
        return self._downloading
    @downloading.setter
    def downloading(self, value):
        self._downloading = value
        StatusCache.update(self.torrent_id, StatusFields.DOWNLOADING, value)

    @property
    def unavailable(self):
        if not hasattr(self, '_unavailable'):
            self.unavailable  = -1                   # Seconds torrent is being downloaded but was unavailable
        return self._unavailable
    @unavailable.setter
    def unavailable(self, value):
        self._unavailable = value
        StatusCache.update(self.torrent_id, StatusFields.DOWNLOAD_UNAVAILABLE, value)

    @property
    def completed(self):
        if not hasattr(self, '_completed'):
            self.completed    = False                # Torrent is completed: succesfully downloaded or failed. Complete event transmitted.
        return self._completed
    @completed.setter
    def completed(self, value):
        self._completed = value

    @property
    def failed(self):
        if not hasattr(self, '_failed'):
            self.failed       = None                 # Torrent is failed to download (True, False, None)
        return self._failed
    @failed.setter
    def failed(self, value):
        self._failed = value

    @property
    def time_added(self):
        if not hasattr(self, '_time_added'):
            self.time_added = None                  # Torrent added timestamp - seconds since 1970 (epoch)
        return self._time_added
    @time_added.setter
    def time_added(self, value):
        self._time_added = value
        StatusCache.update(self.torrent_id, StatusFields.TIME_ADDED, value)

    def __getstate__(self):
        """Prevent pickling of unpickable attributes"""
        state = dict(self.__dict__)
        if 'log' in state:
            del state['log']
        if 'config' in state:
            del state['config']

        return state

