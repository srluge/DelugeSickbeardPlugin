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

class Torrent:

    def __init__(self):
        self.options = {}
        self.options['move_completed_path'] = '/tmp/my_torrent'

        self.magnet = "http://someurl"

    def get_status(self,item):
        return { 'hash': 123456789012,
                 'name': 'my_torrent',
                 'is_finished': True,
                 'num_files': 1,
                 'save_path': '/tmp/my_torrent'
               }

def pprops(display,obj):
    log.debug("--- BEGIN: %s", display)
    for name in dir(obj):
        attr = getattr(obj,name)
        if not callable(attr):
            log.debug( "%s: %s", name, attr )
    log.debug("--- END  : %s", display)

def pprops2(display,obj):
    print "--- BEGIN: %s" % display
    for name in dir(obj):
        attr = getattr(obj,name)
        if not callable(attr):
            print "%s: %s" % ( name, attr )
    print "--- END  : %s" % display

def ptorrent(torrent,all=False):
    name = self._torrent_get_name(torrent)

    log.debug("Torrent Name      : %s", name)
    log.debug("torrent_id        : %s", torrent.torrent_id)
    log.debug("filename          : %s", torrent.filename)
    log.debug("magnet            : %s", torrent.magnet)
    log.debug("state             : %s", torrent.state)

    log.debug("Files in torrent  >")
    for f in torrent.get_files():
        log.debug(f)

    if all:
        self.pprops("torrent"             ,torrent)
        self.pprops("torrent.config"      ,torrent.config)
        self.pprops("torrent.status"      ,torrent.status)
        self.pprops("torrent.handle"      ,torrent.handle)
        self.pprops("torrent.torrent_info",torrent.torrent_info)

