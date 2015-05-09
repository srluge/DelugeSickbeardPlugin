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

from deluge.plugins.init import PluginInitBase

class CorePlugin(PluginInitBase):
    def __init__(self, plugin_name):
        from core import Core as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(CorePlugin, self).__init__(plugin_name)

class GtkUIPlugin(PluginInitBase):
    def __init__(self, plugin_name):
        from gtkui import GtkUI as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(GtkUIPlugin, self).__init__(plugin_name)

class WebUIPlugin(PluginInitBase):
    def __init__(self, plugin_name):
        from webui import WebUI as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(WebUIPlugin, self).__init__(plugin_name)
