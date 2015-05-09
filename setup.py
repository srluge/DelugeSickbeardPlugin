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

from setuptools import setup

__plugin_name__      = "Sickbeard"
__version__          = "0.1.0"
__url__              = "https://github.com/srluge/DelugeSickbeardPlugin/blob/master/README.md"
__license__          = "MIT"
__description__      = "Deluge plugin for Sickbeard integration"
__long_description__ = """Automatically process completed or failed downloads with Sickbeard."""
__pkg_data__         = {__plugin_name__.lower(): ["data/*"],
                        '': ["../LICENSE", "../README.md"]}

setup(
    name             = __plugin_name__,
    version          = __version__,
    description      = __description__,
    url              = __url__,
    license          = __license__,
    long_description = __long_description__,

    packages         = [__plugin_name__.lower()],
    package_data     = __pkg_data__,

    entry_points="""[deluge.plugin.core]
%s = %s:CorePlugin
[deluge.plugin.gtkui]
%s = %s:GtkUIPlugin
[deluge.plugin.web]
%s = %s:WebUIPlugin""" % ((__plugin_name__, __plugin_name__.lower())*3)
)
