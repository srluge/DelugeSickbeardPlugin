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

from twisted.internet import reactor, defer
from twisted.web.client import Agent, HTTPConnectionPool
from twisted.web._newclient import ResponseDone
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol

from base64 import b64encode
import re
import sys

import logging

try:
    from urllib        import urlencode
except ImportError:
    from urllib.parse  import urlencode

class BodyCache(Protocol):
    def __init__(self, d):
        self.d     = d
        self.cache = ""

    def dataReceived(self, bytes):
        self.cache = self.cache + bytes

    def connectionLost(self, reason):
        try:
            raise reason.raiseException()
        except ResponseDone as e:
            self.d.callback(self.cache)
        else:
            self.d.errback(reason)

class WebClient:
    """
    Small basic non-blocking Twisted based web client with support for basic
    authentication.
    """

    _USER_AGENT_  = 'Twisted based web client'
    _LOGGER_NAME_ = 'WebClient'

    def __init__(self, logger = None):
        self.d               = None
        self.skip_empty_args = True
        if not None is logger:
            self.log         = logger
        else:
            self.log         = logging.getLogger(WebClient.__name__)

        self.user_agent      = self._USER_AGENT_

    def get(self, base_url, args = {}, username = None, password = None):

        #pool = HTTPConnectionPool(reactor, persistent=True)
        #pool.maxPersistentPerHost = 3
        #pool.retryAutomatically = False

        agent   = Agent(reactor)
        headers = { 'User-Agent': [self._USER_AGENT_] }

        if username:
            authorization            = b64encode(username + ":" + password)
            headers['Authorization'] = [authorization]

        url = self._get_url(base_url, args)

        self.log.info('Requesting URL: %s' % url)

        d_agent  = agent.request(
            'GET',
            url,
            Headers(headers),
            None)

        d_agent.addCallback(self.cb_agent)
        d_agent.addErrback(self.cb_agent_err)

        self.d = defer.Deferred()

        return self.d

    def set_user_agent(self, user_agent):
        self.user_agent = user_agent

    def _get_url(self, base_url, args):
        urlp = {}

        if re.search(r'[?&]', base_url):
            raise ValueError('Base-URL may not contain the characters ? and &.')

        if self.skip_empty_args:
            for name in args:
                if not args[name] ==  None:
                    urlp[name] = args[name]
        else:
            urlp = args

        url = re.sub(r'/+$', '', base_url )

        if urlp:
            url += '?' + urlencode(urlp)

        return url

    def cb_agent(self, response):

        self.log.debug('')
        self.log.debug('Request:')
        self.log.debug(response.request.method + ' ' + response.request.absoluteURI)
        for header, value in response.request.headers.getAllRawHeaders():
            self.log.debug(header + ': ' + str(value))

        self.log.debug('')
        self.log.debug('Response:')
        self.log.debug(str(response.version))
        self.log.debug(str(response.code) + ' ' + str(response.phrase))
        self.log.debug(str(response.length) + ' bytes' )

        for header, value in response.headers.getAllRawHeaders():
            self.log.debug(header + ': ' + str(value))

        d = defer.Deferred()
        response.deliverBody(BodyCache(d))

        d.addCallback(self.cb_body)
        d.addErrback(self.cb_body_err)

    def cb_agent_err(self, failure):
        self.log.error(failure.getErrorMessage())
        self.d.errback(failure)

    def cb_body(self, body):
        for line in body.split('\n'):
            self.log.debug(line)
        self.d.callback(body)

    def cb_body_err(self, failure):
        self.log.error(failure.getErrorMessage())
        self.d.errback(failure)


if __name__ == "__main__":

    def get(result):
        log.info('Success')

    def get_err(failure):
        log.error('Failure')

    def stop(ignored):
        reactor.stop()

    log = logging.getLogger("WebClient")
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

    url    = 'http://' + sys.argv[1] + '/home/postprocess/processEpisode'
    args   = {'quiet': 1, 'dir': '/tmp'}

    for i in range(1):
        log.info("Client" + str(i))
        client = WebClient()
        d      = client.get(url, args)
        d.addCallback(get)
        d.addErrback(get_err)

    reactor.run()
