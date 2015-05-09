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

from log import *

class StatusFields(object):
    ALL      = [ "download_status", "processing_status", "processing_completed_time", "downloading", "download_unavailable", "time_added" ]
    DOWNLOAD_STATUS, PROCESSING_STATUS, PROCESSING_COMPLETED_TIME, DOWNLOADING, DOWNLOAD_UNAVAILABLE, TIME_ADDED = ALL

class StatusCache(object):
    """
    Keep cache of status fields available in UI. This cache is consulted
    N-torrents * N-fields * refresh (once a second or so). Without cache
    100% cpu usage will be used just to provide status information to the
    end user.
    """

    log    = getLogger('deluge.sickbeard.statuscache.StatusCache')
    cache  = {}

    @staticmethod
    def update(torrent_id, field, data, overwrite = True):
        if not torrent_id in StatusCache.cache:
            StatusCache.cache[torrent_id] = {}

        if field in StatusCache.cache[torrent_id] and not overwrite:
            return

        StatusCache.log.debug("Updating %s for torrent %s with value %s" %(field, torrent_id, data))

        StatusCache.cache[torrent_id][field] = data

    @staticmethod
    def delete(torrent_id):
        if torrent_id in StatusCache.cache:
            c = StatusCache.cache
            del c[torrent_id]

    @staticmethod
    def get(torrent_id, field):
        result = None
        try:
            result = StatusCache.cache[torrent_id][field]
        finally:
            return result
