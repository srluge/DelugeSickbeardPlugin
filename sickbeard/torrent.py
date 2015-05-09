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

import os

class TorrentMode:
    ALL      = [ "SINGLE-FILE", "MULTI-FILE", "UNKNOWN" ]
    SINGLE_FILE, MULTI_FILE, UNKNOWN = ALL
    DEFAULT  = MULTI_FILE

class TorrentInfo:
    """Small wrapper class for accessing aspects of torrents as registered by deluge"""

    @staticmethod
    def get_id(torrent):
        """Return the hash id of torrent

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          string: Hash id of torrent
        """

        return torrent.get_status(["hash"])["hash"]

    @staticmethod
    def get_display_name(torrent):
        """Return the name of torrent

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          string: Display name of torrent
        """

        return torrent.get_status(["name"])["name"] if torrent else None

    @staticmethod
    def is_finished(torrent):
        """Return the torrents status

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          bool: True if torrent finished downloading. False if not.
        """

        return torrent.get_status(["is_finished"])["is_finished"]

    @staticmethod
    def paused(torrent):
        """Return torrent pause status

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          bool: Torrent pause status
        """

        return torrent.get_status(["paused"])["paused"]

    @staticmethod
    def state(torrent):
        """
        Return Libtorrent torrent state. For example:

        Queued, Checking, Downloading, Error, ...

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          string: in common.py/LT_TORRENT_STATE
        """

        return torrent.get_status(["state"])["state"]

    @staticmethod
    def get_num_files(torrent):
        """Wrapper to return number of downloaded files in torrent

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          int: Number of downloaded files in torrent
        """

        return torrent.get_status(["num_files"])["num_files"]

    @staticmethod
    def get_mode(torrent):
        """
        Returns if torrent contains a single file or a directory
        with one or more files.

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          TorrentMode: Single- or multi-file, or unknown
        """

        files = torrent.torrent_info.files()

        if not files or len(files) == 0:
            return TorrentMode.UNKNOWN

        for f in files:
            if "/" in f.path:
                return TorrentMode.MULTI_FILE

        return TorrentMode.SINGLE_FILE

    @staticmethod
    def get_move_completed_path(torrent):
        """Return path torrent is moved to(if any) after download completion

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          string: Sickbeard id(name) of torrent
        """

        return torrent.options["move_completed_path"]

    @staticmethod
    def get_save_path(torrent):
        """Return the save path. During downloading this may be another path
           then the path after the copnfigurable final move.

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          string: Save path content of downloaded torrent
        """

        return torrent.get_status(["save_path"])["save_path"]

    @staticmethod
    def get_saved_path(torrent):
        """Return the path torrent currently is saved.

        SINGLE_FILE torrent: <save-path>
        MULTI-FILE  torrent: <save-path>/<name-torrent>

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          string: Path containing downloaded torrent content
        """

        path = TorrentInfo.get_save_path(torrent)
        name = TorrentInfo.get_display_name(torrent)
        mode = TorrentInfo.get_mode(torrent)

        if  mode == TorrentMode.MULTI_FILE:
            path += "/" + name

        return path.replace("//","/")

    @staticmethod
    def get_distributed_copies(torrent):
        """
        Return torrent availability

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          float: 'The number of distributed copies of the file. note that one
                 copy may be spread out among many peers. This is a floating
                 point representation of the distributed copies. the integer
                 part tells how many copies there are of the rarest piece(s)
                 the fractional part tells the fraction of pieces that have
                 more copies than the rarest piece(s).'
                 http://www.libtorrent.org/reference-Core.html
        """
        return torrent.get_status(["distributed_copies"])["distributed_copies"]

    @staticmethod
    def get_time_added(torrent):
        """
        Return the time torrent was added

        Args:
          torrent (deluge.core.torrent): Torrent

        Returns:
          int: Seconds since 1970 (epoch)
        """

        return torrent.get_status(["time_added"])["time_added"]
