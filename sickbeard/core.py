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
import logging.handlers
import deluge.component        as component

from sickbeard                 import *
from log                       import *
from deluge.configmanager      import *
from deluge.plugins.pluginbase import CorePluginBase
from deluge.core.rpcserver     import export
from deluge.core.rpcserver     import DelugeError
from webclient                 import *
from twisted.internet.defer    import inlineCallbacks, returnValue
from convert                   import *
from events                    import *
from manager                   import *
from statuscache               import *

DEFAULT_PREFS = {
    'ssl'              : False,
    'host'             : 'localhost',
    'port'             : 8081,
    'username'         : '',
    'password'         : '',
    'method'           : ProccessMethod.DEFAULT,
    'quiet'            : True,
    'force'            : False,
    'priority'         : False,
    'workers'          : 3,
    'failed'           : False,       # Automatic failed processing enabled
    'failed_interval'  : 60,          # Check availability torrent every N seconds
    'failed_limit'     : 16,          # Process as failed if torrent is downloading, but unabailable longer then N hours
    'failed_time'      : 24,          # Process as failed if torrent is downloading longer then N hours
    'failed_label'     : True,        # Limit failed detection to torrents with configured label
    'failed_label_name': 'sickrage',  # Labelname
    'remove'           : False,
    'remove_data'      : False,
}

class Core(CorePluginBase):

    # Plugin is enabled/activated on startup or on plugin enable from UI
    def enable(self):

        self.log_handlers = []
        self.init_logging()

        self.log.info('Initializing Sickbeard plugin.')

        self.config        = ConfigManager("sickbeard.conf", DEFAULT_PREFS)

        self.eventmanager  = component.get("EventManager")
        self.pluginmanager = component.get('CorePluginManager')

        self.sickbeard     = Sickbeard(self.config)
        self.manager       = Manager(self.config, self.sickbeard)

        self.log.info('Enabling Sickbeard plugin.')

        self.pluginmanager.register_status_field('sickbeard_download_status'          , self.get_field_download_status)
        self.pluginmanager.register_status_field('sickbeard_processing_status'        , self.get_field_processing_status)
        self.pluginmanager.register_status_field('sickbeard_processing_completed_time', self.get_field_processing_completed_time)
        self.pluginmanager.register_status_field('sickbeard_downloading'              , self.get_field_downloading)
        self.pluginmanager.register_status_field('sickbeard_download_unavailable'     , self.get_field_download_unavailable)
        self.pluginmanager.register_status_field('sickbeard_time_added'               , self.get_field_time_added)

        self.manager.start()

    # Plugin is disabled/dectivated on shutdown or on plugin disable from UI. Note that
    # any tasks in the worker queue will be finished in the background.
    def disable(self):

        self.log.info('Disabling Sickbeard plugin.')

        self.manager.stop()

        self.pluginmanager.deregister_status_field('sickbeard_failed')
        self.pluginmanager.deregister_status_field('sickbeard_process_status')
        self.pluginmanager.deregister_status_field('sickbeard_process_completed_time')
        self.pluginmanager.deregister_status_field('sickbeard_downloading')
        self.pluginmanager.deregister_status_field('sickbeard_download_unavailable')
        self.pluginmanager.deregister_status_field('sickbeard_time_added')

        self.deinit_logging()

    def init_logging(self):
        # Get custom logger
        log = getLogger('deluge.sickbeard')

        # Do not propagate to higher level handlers
        log.propagate = False

        log.setLevel(logging.DEBUG)

        # File handler with dispatching formatter
        logfile = deluge.configmanager.get_config_dir("sickbeard.log")
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1000000, backupCount=4)
        handler.setFormatter(DispatchingFormatter([ TaskFormatter(), DefaultFormatter() ]))
        log.addHandler(handler)
        self.log_handlers.append(handler)

        # Task handler
        handler = TaskHandler()
        handler.setFormatter(TaskFormatter())
        log.addHandler(handler)
        self.log_handlers.append(handler)

        getLogger('deluge.sickbeard.SickbeardWorker.WebClient').setLevel(logging.ERROR)
        self.log = getLogger('deluge.sickbeard.Core')

    def deinit_logging(self):
        log = getLogger('deluge.sickbeard')

        log.setLevel(logging.NOTSET)

        for handler in self.log_handlers:
            log.removeHandler(handler)

    def get_field_download_status(self, torrent_id):
        failed = StatusCache.get(torrent_id, StatusFields.DOWNLOAD_STATUS)

        if not failed is None:
            return "completed" if not failed else "failed"
        else:
            return None

    def get_field_processing_status(self, torrent_id):
        stat = StatusCache.get(torrent_id, StatusFields.PROCESSING_STATUS)

        if stat is None:
            return TaskStatus.NONE

        task_id, status = stat

        if not task_id is None:
            return status + '_' + task_id
        else:
            return None

    def get_field_processing_completed_time(self, torrent_id):
        time = StatusCache.get(torrent_id, StatusFields.PROCESSING_COMPLETED_TIME)

        if time is None:
            time = 9999999999

        return time

    def get_field_downloading(self, torrent_id):
        return StatusCache.get(torrent_id, StatusFields.DOWNLOADING)

    def get_field_download_unavailable(self, torrent_id):
        return StatusCache.get(torrent_id, StatusFields.DOWNLOAD_UNAVAILABLE)

    def get_field_time_added(self, torrent_id):
        time = StatusCache.get(torrent_id, StatusFields.TIME_ADDED)

        if time is None:
            time = 9999999999

        return time

    @export
    def set_config(self, config):
        """Sets the config dictionary"""

        for key in config.keys():
            self.config[key] = config[key]

        self.config.save()

        self.eventmanager.emit(SickbeardConfigChangedEvent())

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config

    @export
    def add(self, varg, failed):
        """Add torrent(s) for postprocessing to JobQueue"""
        return self.sickbeard.add(varg, failed)

    @export
    def get_jobs(self):
        return self.sickbeard.get_jobs()

    @export
    def get_task(self,task_id):
        return self.sickbeard.get_task(task_id)

    @export
    def get_tasks(self, reverse = True):
        return self.sickbeard.get_tasks()

    @export
    def get_patterns(self):
        """
        Return Sickbeard post-process output success and error search
        patterns. These patters are use to detect wether a call to
        sickbeard succeeded to failed.
        """
        return {
                 'success': SickbeardWorker.SUCCESS,
                 'error'  : SickbeardWorker.ERRORS
               }

    @export
    @inlineCallbacks
    def test_connection(self, config):
        """Test connection to Sickbeard"""
        result = { 'success': False, 'data': None }

        try:
            self.log.info("Testing connection")

            base_url = SickbeardWorker.get_base_url(config)
            logger   = getLogger('deluge.sickbeard.Core.WebClient')
            logger.setLevel(logging.INFO)
            client   = WebClient(logger)
            data     = yield client.get(base_url, args = {'dir': 'not-a-dir'}, username = self.config['username'], password = self.config['password'])

            if data.count('Postprocessing result') > 0:
                result['success'] = True
                self.log.info("Connection test succeeded")
            else:
                result['success'] = False
                result['data']    = todict(data)
                self.log.error("Connection test failed: %s" % str(data))

        except Exception, e:
            result['success'] = False
            result['data']    = todict(str(e))

            self.log.error("Connection test failed: %s" % str(e))

        returnValue(result)

    @export
    def get_post_process_methods(self):
        """
        Return option list of all Sickbeard post-processing methods

        {
           methods: [
              { method: <method code>, translation: <method translation> },
              ...
           ]
        }
        """
        json    = { 'methods': [] }
        methods = ProccessMethod.getTranslations()

        for code, translation in methods.iteritems():
            json['methods'].append({'method': code, 'translation': translation})

        return json

