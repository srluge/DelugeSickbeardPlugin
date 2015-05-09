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

from log                   import *
from events                import *
from torrent               import *
from detect                import *
from status                import *
from statusdb              import *

import deluge.component as component

class Manager(object):
    """
    Manage status of torrents.
    """

    def __init__(self, config, sickbeard):

        super(Manager, self).__init__()

        self.log          = getLogger('deluge.sickbeard.manager.Manager')

        self.log.info("Initializing manager")

        self.config       = config
        self.sickbeard    = sickbeard

        self.eventmanager = component.get("EventManager")
        self.manager      = component.get("TorrentManager")

        Status.config     = self.config
        self.statusdb     = StatusDatabase()

        self.detect_loop = DetectionLoop(self.config, self.statusdb)

    def __del__(self):
        if hasattr(self, 'log'):
            self.log.info("Deleting manager")

        if hasattr(self, 'failed_loop'):
            self.failed_loop.stop()

    def register(self, name, callback):
        self.log.info('Registering event %s.' % name)
        self.eventmanager.register_event_handler(name,callback)

    def deregister(self, name, callback):
        self.log.info('Deregistering event %s.' % name)
        self.eventmanager.deregister_event_handler(name,callback)

    def on_finished(self, torrent_id):
        self.log.info("Torrent finished event: %s", torrent_id)

        if torrent_id in self.statusdb:
            status = self.statusdb[torrent_id]
        else:
            status = Status(torrent)

        status.update()

    def on_completed(self, status):
        self.log.debug("Torrent competed event: %s (failed=%s)", status.torrent_id, status.failed)

        self.sickbeard.add_job_by_id(status.torrent_id, status.failed)

    def unmanage(self, torrent):
        pass

    def get_status(self, torrent_id):
        return self.statusdb[torrent_id]

    def start(self):

        self.log.info("Starting manager")

        self.register("TorrentFinishedEvent"    , self.on_finished)
        self.register("SickbeardStatusCompleted", self.on_completed)

        # note: detection loop is automatically started when Deluge
        #       finished starting. See DetectionLoop.on_session_started.

    def stop(self):

        self.log.info("Stopping manager")

        self.detect_loop.stop()

        self.deregister("TorrentFinishedEvent"    , self.on_finished)
        self.deregister("SickbeardStatusCompleted", self.on_completed)
