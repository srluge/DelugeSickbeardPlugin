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

from twisted.internet.task import LoopingCall
from log                   import *
from events                import *
from torrent               import *
from status                import *
from statuscache           import *

import deluge.component as component

class DetectionLoop(LoopingCall):
    """
    Looping call periodically checking the download status of torrents.
    Automatically detects if downloads are failed based.
    """

    def __init__(self, config, statusdb):

        super(DetectionLoop, self).__init__(self.process)

        self.config          = config
        self.statusdb        = statusdb

        self.manager         = component.get("TorrentManager")
        self.eventmanager    = component.get("EventManager")
        self.pluginmanager   = component.get("CorePluginManager")

        self.torrents        = self.manager.torrents

        self.log             = getLogger('deluge.sickbeard.detect.DetectionLoop')

        self.started         = False
        self.session_started = False

        self.register("SickbeardConfigChangedEvent", self.on_config_change)
        self.register("SessionStartedEvent", self.on_session_started)

    def __del__(self):

        self.deregister("SickbeardConfigChangedEvent", self.on_config_change)
        self.deregister("SessionStartedEvent", self.on_session_started)
        self.stop()

        super(LoopingCall, self).__init__()

    def register(self, name, callback):
        self.log.info('Registering event %s.' % name)
        self.eventmanager.register_event_handler(name, callback)

    def deregister(self, name, callback):
        self.log.info('Deregistering event %s.' % name)
        self.eventmanager.deregister_event_handler(name, callback)

    def process(self):
        """
        Automatically detect failed downloads and post-process them with
        Sickbeard.
        """
        if self.session_started:

            self.log.debug("Analyzing per torrent download status")

            for torrent_id in self.torrents:
                if not torrent_id in self.statusdb:
                    self.log.info("Adding torrent %s to status database", str(torrent_id))

                    status = Status(self.torrents[torrent_id])
                    self.statusdb.update(status)

            for torrent_id, status in self.statusdb.iteritems():
                if not torrent_id in self.torrents:
                    self.log.info("Removing torrent %s from status database", str(torrent_id))
                    self.statusdb.delete(torrent_id)
                else:
                    status.update()

            # Save changed status to disk
            self.statusdb.sync()

    def stop(self):

        if self.started == True:
            self.log.info("Stopping automatic failed processing.")
            super(DetectionLoop, self).stop()
            self.started = False

    def start(self):

        if not self.session_started:
            self.log.error("Attempt to start failed processing while deluge is not fully started.")
            return

        label_plugin_required = self.config['failed_label']

        if label_plugin_required and 'Label' not in self.pluginmanager.get_enabled_plugins():
            self.log.info("Not starting failed processing. Required label plugin (as per config) not enabled. %s", str(self.pluginmanager.get_enabled_plugins()))
            return

        # Start failed processing if enabled
        if self.config['failed'] == True:
            self.log.info("Starting automatic failed processing (repeated every %s sec).", self.config['failed_interval'])
            d = super(DetectionLoop, self).start(self.config['failed_interval'])
            self.started = True
            d.addErrback(self.error)

    def error(self, failure):
        for line in failure.getTraceback().split('\n'):
            self.log.error("%s" % line)

    def restart(self):

        self.stop()
        self.start()

    def on_config_change(self):

        self.log.debug("Configuration changed")
        self.restart()

    def on_session_started(self):

        self.log.debug("Session started")
        self.session_started = True

        self.start()
