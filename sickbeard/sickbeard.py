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

import deluge.component as component
import convert          as conv

from log                    import *
from types                  import *
from torrent                import TorrentInfo
from sickbeard_worker       import *
from tasklog                import *

from collections            import OrderedDict


class Sickbeard:
    """Deluge to Sickbeard integration.

    Notify Sickbeard to post-process completed/failed torrent(s). Post-process requests for
    torrents are queued and handled asynchronously to not block the deluge server main
    thread.
    """

    def __init__(self, config):
        self.config             = config
        self.manager            = component.get("TorrentManager")
        self.torrents           = self.manager.torrents
        self.tasklog            = Tasklog()

        self.log                = getLogger('deluge.sickbeard.Sickbeard')

        # Configure workers
        SickbeardWorker.config  = config
        SickbeardWorker.manager = self.manager
        SickbeardWorker.tasklog = self.tasklog

        # Setup processing queue with workers
        num_workers             = self.config['workers']
        self.taskq              = SickbeardWorkerQueue(num_workers, log_status = True, log_interval = 1)

    def add(self, varg, failed):
        """Add torrent(s) by id for post-processing to JobQueue"""
        self.log.info("Add torrent(s) for post-processing to job-queue: %s", varg)
        self.log.info("Type  : " + str(type(varg)))
        self.log.info("Failed: " + str(failed))
        success = True
        if type(varg) is TupleType:
            torrents = varg
            for torrent_id in torrents:
                if not self.add_job_by_id(torrent_id, failed):
                    success = False
        else:
            torrent_id = varg
            if not self.add_job_by_id(torrent_id, failed):
                success = False;

        return success;

    def add_job_by_id(self, torrent_id, failed):
        self.log.debug("Add new job to queue (%s)", torrent_id)
        if torrent_id in self.torrents:
            torrent = self.torrents[torrent_id]

            return self.add_job(torrent, failed);

        else:
            self.log.debug("Can't add new job to queue. Torrent with id %s is not available (anymore).", torrent_id)

        return False

    def add_job(self, torrent, failed):
        name = TorrentInfo.get_display_name(torrent)
        self.log.debug("Add new job to queue (%s)", name)

        id = TorrentInfo.get_id(torrent)
        if id == name:
            self.log.debug("Torrent(%s) not ready. No torrent(release) name (yet) available. Sickbeard post-processing requires a correct torrent name.", name)
            return False

        if failed:
            # Pause torrent and disable auto managed to prevent torrent from
            # being picked up again at a later point
            torrent.pause()
            self.log.debug("Torrent(%s) set to 'pause' to prepare for Sickbeard post-processing.", name)
        else:
            if not TorrentInfo.is_finished(torrent):
                self.log.debug("Torrent(%s) not finished. Adding job to queue not allowed.", name)
                return False

            # Set torrent to paused; sickbeard soon may move/copy/link it
            torrent.pause()
            self.log.debug("Torrent(%s) paused to prepare for Sickbeard post-processing.", name)

        task = Task(torrent)
        if not task in self.taskq:
            task.failed = failed
            self.taskq.put(task)
            return True
        else:
            self.log.warning("Torrent(%s) already added to queue")
            return False

    def get_tasks(self, ordered = True, reverse = True, convert = True):
        """
        Return dictionary containing copy of all tasks. Indexed by task id
        and optionally sorted by task start time. Objects are optionally
        converted to dictionaries to prevent later marshalling to fail.

        WARNING: relatively slow function
        """

        tasks   = self.taskq.get_all()         # Dict tasks currently pending/worked on

        tasks.update(self.tasklog.get_all())   # Add dict tasks from task log

        if not ordered:
            return tasks

        sort  = sorted(tasks.iteritems(), key=lambda x: x[1].start_time, reverse=reverse)
        odict = OrderedDict(sort)

        # Convert object deep in dict to dicts. Deluge marshalling does not
        # support objects.
        if convert:
            return conv.no_underscore( conv.todict(odict) )
        else:
            return odict

    def get_task(self, task_id, convert = True):
        """
        Return task object by task id. Objects can optionally be converted
        to dictionaries to prevent later marshalling to fail.
        """

        tasks = self.get_tasks(ordered = False)

        if task_id in tasks:
            if convert:
                return conv.no_underscore( conv.todict(tasks[task_id]) )
            else:
                return task[task_id]
        else:
            return False
