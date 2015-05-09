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

import uuid
import time
import os

if os.environ.get('DEBUG_DELUGE') == '1':
    from debug               import Torrent
else:
    from deluge.core.torrent import Torrent

from sickbeard_worker        import *
from torrent                 import TorrentInfo
from statuscache             import *

class TaskStatus:
    ALL      = [ "queued", "processing", "success", "failed", "none" ]
    QUEUED, PROCESSING, SUCCESS, FAILED, NONE  = ALL
    DEFAULT  = QUEUED

class TaskScheduleType:
    ALL      = [ "none", "automatic", "manual" ]
    NONE, AUTOMATIC, MANUAL = ALL
    DEFAULT  = NONE

class TorrentLogInfo(object):
    """Copy of relevant torrent information. Used to save to disk."""

    def __init__(self, torrent):

        if not isinstance(torrent, Torrent):
            raise TypeError("Object not instance of class Torrent")

        self.id      = TorrentInfo.get_id(torrent)
        self.name    = TorrentInfo.get_display_name(torrent)
        keys = [
            # dict keys
            "active_time",
            "all_time_download",
            "compact",
            "distributed_copies",
            "download_payload_rate",
            "file_priorities",
            "hash",
            "is_auto_managed",
            "is_finished",
            "max_connections",
            "max_download_speed",
            "max_upload_slots",
            "max_upload_speed",
            "message",
            "move_on_completed_path",
            "move_on_completed",
            "move_completed_path",
            "move_completed",
            "next_announce",
            "num_peers",
            "num_seeds",
            "paused",
            "prioritize_first_last",
            "progress",
            "remove_at_ratio",
            "save_path",
            "seeding_time",
            "seeds_peers_ratio",
            "seed_rank",
            "state",
            "stop_at_ratio",
            "stop_ratio",
            "time_added",
            "total_done",
            "total_payload_download",
            "total_payload_upload",
            "total_peers",
            "total_seeds",
            "total_uploaded",
            "total_wanted",
            "tracker",
            "trackers",
            "tracker_status",
            "upload_payload_rate",

            # functions
            "comment",
            "eta",
            "file_progress",
            "files",
            "is_seed",
            "name",
            "num_files",
            "num_pieces",
            "peers",
            "piece_length",
            "private",
            "queue",
            "ratio",
            "total_size",
            "tracker_host"
        ]
        self.status  = torrent.get_status(keys)
        self.options = torrent.options
        self.magnet  = torrent.magnet

class Task(object):
    """Sickbeard port-processing task"""

    def __init__(self, torrent):

        if not isinstance(torrent, Torrent):
            raise TypeError("Object not instance of class Torrent")

        self.id              = str(uuid.uuid4());           # Unique ID of job
        self.start_time      = int(time.time())             # Start time job - seconds since 1970 (epoch)
        self._completed_time = None                         # End   time job - seconds since 1970 (epoch)
        self.schedule_type   = TaskScheduleType.NONE        # Automatically scheduled or manually
        self.torrent         = torrent                      # Reference to deluge Torrent object
        self._torrent_info   = TorrentLogInfo(torrent)      # Persistable torrent info
        self._status         = TaskStatus.NONE              # Job status
        self.output          = []                           # Sickbeard post processing output

        self._failed         = False                        # Failed download
        self.force           = False                        # Force already Post Processed Dir/Files
        self.priority        = False                        # Mark Dir/Files as priority download

        self.persisted       = False                        # Persisted to disk

        self.worker_id       = None                         # Worker assigned to task
        self.worker_seq      = None                         # Worker task sequence id

        self.log             = logging.getLogger('task')    # Retrieve default logger

    def initialize(self):
        StatusCache.update(self.torrent_info.id, StatusFields.DOWNLOAD_STATUS          , self.failed)
        StatusCache.update(self.torrent_info.id, StatusFields.PROCESSING_STATUS        , (self.id, self.status))
        StatusCache.update(self.torrent_info.id, StatusFields.PROCESSING_COMPLETED_TIME, self.completed_time)

    def finalize(self):
        StatusCache.update(self.torrent_info.id, StatusFields.PROCESSING_STATUS        , (None, None))
        StatusCache.update(self.torrent_info.id, StatusFields.PROCESSING_COMPLETED_TIME, "none")
        StatusCache.update(self.torrent_info.id, StatusFields.DOWNLOAD_STATUS          , "none")

    @property
    def completed_time(self):
        return self._completed_time
    @completed_time.setter
    def completed_time(self, value):
        self._completed_time = value
        StatusCache.update(self.torrent_info.id, StatusFields.PROCESSING_COMPLETED_TIME, value)

    @property
    def torrent_info(self):
        return self._torrent_info
    @torrent_info.setter
    def torrent_info(self, value):
        self._torrent_info = value

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        self._status = value
        StatusCache.update(self.torrent_info.id, StatusFields.PROCESSING_STATUS, (self.id, value))

    @property
    def failed(self):
        return self._failed
    @failed.setter
    def failed(self, value):
        self._failed = value
        StatusCache.update(self.torrent_info.id, StatusFields.DOWNLOAD_STATUS, value)

    def __getstate__(self):
        """Prevent pickling of unpickable attributes"""
        state = dict(self.__dict__)
        if 'log' in state:
            del state['log']
        if 'torrent' in state:
            del state['torrent']

        return state

if __name__ == "__main__":
    pass
    # note: use task_dump.py for further debugging

