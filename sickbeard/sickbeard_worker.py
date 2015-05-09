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
import sys
import error

from twisted.internet       import defer, reactor
from twisted.internet.defer import inlineCallbacks

from task                   import *
from torrent                import *
from webclient              import *
from worker                 import *
from log                    import getLogger, TaskLoggerAdapter
from tasklog                import *

class ProccessType:
    """Sickbeard API processing type"""
    ALL      = [ "auto", "manual" ]
    AUTOMATIC, MANUAL = ALL
    DEFAULT  = AUTOMATIC

class ProccessMethod:
    """Sickbeard API processing method"""
    ALL         = [ "default"          , "copy", "move", "hardlink", "symlink" ]
    TRANSLATION = [ 'Sickbeard Default', 'Copy', 'Move', 'Hardlink', 'Symlink' ]
    SB_DEFAULT, COPY, MOVE, HARDLINK, SYMLINK = ALL
    DEFAULT     = SB_DEFAULT

    @staticmethod
    def getTranslations():
        """Returns dictionary containing translation for each option"""
        tr = {}
        for i in range(0, len(ProccessMethod.ALL)):
            tr[ProccessMethod.ALL[i]] = ProccessMethod.TRANSLATION[i]

        return tr


class SickbeardWorker(Worker):
    """
    Call Sickbeard API to post-process a torrent

    Run Sickbeard post-processing in a controlled way making sure that both
    the Deluge daemon as well as Sickbeard are not taking up all system
    resources for post-processing. Espcially Deluge daemon's main priority
    should remain downloading torrents.
    """

    manager             = None   # Deluge torrent manager
    config              = None   # Sickbeard deluge plugin configuration
    tasklog             = None   # Log completed tasks

    logger              = getLogger('deluge.sickbeard.SickbeardWorker')
    logger_webclient    = getLogger('deluge.sickbeard.SickbeardWorker.WebClient')

    _PATH_POSTPROCESS   = "/home/postprocess/processEpisode"

    ERRORS              = [
                            'Processing failed for',
                            'Validator',
                            'Failed Download Processing failed',
                            'Problem(s) during processing',
                            'Error:'
                          ]

    SUCCESS             = [
                            'Processing succeeded for',
                            'Failed Download Processing succeeded',
                            'Successfully processed',
                            "You're trying to post process a video that's already been processed, skipping"
                          ]

    def __init__(self, dqueue):

        super(SickbeardWorker, self).__init__(dqueue)

        if SickbeardWorker.manager is None or \
           SickbeardWorker.config  is None or \
           SickbeardWorker.tasklog is None:
            raise TypeError("SickbeardWorker requires a valid manager, config and tasklog object.")

        self.task  = None
        self.log   = SickbeardWorker.logger
        self.tlog  = TaskLoggerAdapter(SickbeardWorker.logger)
        self.tlog.set_task(self.task)
        self.wlog  = TaskLoggerAdapter(SickbeardWorker.logger_webclient)
        self.wlog.set_task(self.task)

    @inlineCallbacks
    def work(self, task):

        task.status = TaskStatus.PROCESSING
        tid         = task.torrent_info.id

        try:
            # Store pointer to task
            self.task = task

            # Save worker info to task
            self.task.worker_id  = self.id
            self.task.worker_seq = self.seq

            # Initialize logger adapter with task being worked on
            self.tlog.set_task(self.task)
            self.wlog.set_task(self.task)

            torrent   = task.torrent
            name      = TorrentInfo.get_display_name(torrent)
            id        = TorrentInfo.get_id(torrent)

            self.tlog.info("post-process torrent(%s)" % name)

            if torrent is None:
                self.tlog.error("torrent with id '%s' is no longer with us anymore." % id)
                defer.returnValue(False)

            result      = yield self.call_sickbeard(task)
            task.status = TaskStatus.SUCCESS if result else TaskStatus.FAILED

            remove, remove_data = (self.config['remove'], self.config['remove_data'])
            if result and remove:
                self.tlog.info("schedule torrent(%s) for removal" % name)
                self.manager.remove(id, remove_data)
            else:
                self.tlog.info("*skip* schedule torrent(%s) for removal" % name)

            log_level = logging.INFO if result else logging.ERROR
            self.tlog.log(log_level, "post-process status %s" % task.status)

        except Exception as e:
            result      = False
            task.status = TaskStatus.FAILED

            self.tlog.error('Exception occurred while processing torrent: ' + str(e))
            for line in error.format_exception():
                self.tlog.error("%s" % line)
        finally:
            self.tasklog.add(task)
            defer.returnValue(result)

    @inlineCallbacks
    def call_sickbeard(self, task):
        """
        Call Sickbeard to post-process torrent.

        Sickbeard post-processing API:

        dir        : Directory to be post-processed by Sickbeard
                     SINGLE-FILE torrent: download-complete-path
                     MULTI-FILE  torrent: download-complete-path/name (see spec below)
        nzbname    : name of torrent to be post-processed by Sickbeard
        quiet      : Output type
                     1    : no HTML output
                     unset: HTML output by Sickbeard
        type       : Sickbeard type of post-processing
                     manual: Scheduled Post Processing (Processes files and dirs in TV_DOWNLOAD_DIR)
                     auto  : Script Post Processing (Processes files in a specified directory. Supports single file torrent.)
        force      : Force already Post Processed Dir/Files (on | unset)
        is_priority: Mark Dir/Files as priority download (on | unset)
          (Replace the file, even if it already exists at higher quality)
        failed     : Mark download as failed (1 or 0)
        method     : copy, move, hardlink or symlink

        Sickbeard uses the "nzbname" to look for a "resource" in the post-processing
        directory(dir). A "resource" is either a single video file file, or a directory
        with video files. This to support SINGLE-FILE and MULTI-FILE torrents.

        During post-processing this "resource" is first looked up in the "history"
        table to quickly associate the "resource" to a tv-show, seasion, episode. In case
        no "resource" is available in the history, Sickbeard falls back to scan the
        post-processing directory(dir) for files and directories containing video files
        and use its default naming parse to extract tv-show, seasion, episode details
        from the directory and vide file names it discovered. This is very convenient
        in case we manually downloaded torrents and still want them to be post-processed
        with Sickbeard.

        Failed downloading uses a release name, stored in a separate history table in the


        SINGLE-FILE torrent spec:
          name: the filename. This is purely advisory. (string)
        MULTI-FILE  torrent spec:
          name: the file path of the directory in which to store all the files.
                This is purely advisory. (string)

        Deluge follows the Torrent specifcation advisory.

        Returns:
          bool: True on success. False otherwise.
        """

        try:
            torrent = task.torrent

            dir  = TorrentInfo.get_saved_path(torrent)
            name = TorrentInfo.get_display_name(torrent)
            mode = TorrentInfo.get_mode(torrent)
            id   = TorrentInfo.get_id(torrent)

            params                   = {}
            params['dir']            = dir.encode('utf-8')
            params['nzbName']        = name.encode('utf-8')
            params['quiet']          = 1 if self.config["quiet"] else None

            params['type']           = ProccessType.AUTOMATIC
            params['process_method'] = self.config["method"] if self.config["method"] != ProccessMethod.SB_DEFAULT else None
            params['force']          = "on" if self.config["force"]    or task.force    else None
            params['is_priority']    = "on" if self.config["priority"] or task.priority else None
            params['failed']         = 1 if task.failed else 0

            base_url = self.get_base_url()

            self.tlog.info("Contacting Sickbeard for post-processing")
            self.tlog.info("Torrent(nzbname): %s" % name)
            self.tlog.info("Using base URL  : %s" % base_url)
            self.tlog.info("Username        : %s" % self.config['username'])
            self.tlog.info("Request Type    : %s" % params['type'])
            self.tlog.info("Directory       : %s" % params['dir'])
            self.tlog.info("Mode            : %s" % mode)
            methodDisplay = self.config["method"] if self.config["method"] != ProccessMethod.SB_DEFAULT else "Sickbeard Default"
            self.tlog.info("Method          : %s" % methodDisplay)
            self.tlog.info("Priority        : %s" % self.config["priority"])
            self.tlog.info("Failed          : %s" % params['failed'])
            self.tlog.info("Quiet           : %s" % self.config["quiet"])

            # Downloaded content directory/file must exist, even if it download actually failed, in order
            # for Sickbeard to be able to process the torrent
            if mode == TorrentMode.MULTI_FILE and not os.path.isdir(dir):
                os.makedirs(dir)
            elif mode == TorrentMode.SINGLE_FILE and not os.path.isfile(dir + "/" + name):
                open(dir + "/" + name, 'a').close()

            client  = WebClient(self.wlog)
            result  = yield client.get(base_url, args = params, username = self.config['username'], password = self.config['password'])
        except Exception as e:
            result = False

            self.tlog.error('Exception occurred while processing torrent: ' + str(e))
            for line in error.format_exception():
                self.tlog.error("%s" % line)

        errors  = 0
        success = 0
        if result:
            self.tlog.info("%s bytes received:" % len(result))

            for line in result.split('\n'):
                self.tlog.info("  %s" % line)
                if line:
                    for pattern in SickbeardWorker.ERRORS:
                        errors  += line.count(pattern)
                    for pattern in SickbeardWorker.SUCCESS:
                        success += line.count(pattern)

        succeeded = True if errors == 0 and success >= 1 else False

        if succeeded:
            self.tlog.info("Sickbeard post-processing torrent(%s) succeeded" % name)
        else:
            self.tlog.info("Sickbeard post-processing torrent(%s) failed" % name)

        defer.returnValue(succeeded)

    @staticmethod
    def get_base_url(config = None):

        if not config:

            if SickbeardWorker.manager is None or \
               SickbeardWorker.config  is None or \
               SickbeardWorker.tasklog is None:
                raise TypeError("SickbeardWorker requires a valid manager, config and tasklog object.")

            config = SickbeardWorker.config

        proto    = 'https' if config['ssl'] else 'http'

        base_url = proto            + '://' \
                 + config['host' ]  + ':'   \
                 + str(config['port'])         \
                 + SickbeardWorker._PATH_POSTPROCESS

        return bytes(base_url)


class SickbeardWorkerQueue(WorkerQueue):
    """
    Sickbeard post-processing queue with tasks. Creates SickbeardWorker instances
    to perform the actual work.

    Run Sickbeard post-processing in a controlled way making sure that both
    the Deluge daemon as well as Sickbeard are not taking up all system
    resources for post-processing. Espcially Deluge daemon's main priority
    should remain downloading torrents.
    """

    def __init__(self, num_workers, log_status = False, log_interval = WorkerQueue._LOG_INTERVAL):

        self.log = getLogger('deluge.sickbeard.SickbeardWorkerQueue')
        super(SickbeardWorkerQueue, self).__init__(SickbeardWorker, num_workers, log_status, log_interval)

    def put(self, task):

        if not isinstance(task, Task):
            raise TypeError('Instance not of class Task')

        task.status = TaskStatus.QUEUED
        return super(SickbeardWorkerQueue, self).put(task)

    def __contains__(self, task):

        return task.id in self.get_all()

if __name__ == "__main__":

    logging.getLogger('WebClient').setLevel(logging.INFO)

    from log import getLogger, DispatchingFormatter, TaskFormatter, DefaultFormatter, TaskHandler

    # Get custom logger
    log = getLogger('deluge.sickbeard')

    # Do not propagate to higher level handlers
    log.propagate = False

    log.setLevel(logging.DEBUG)

    # File handler with dispatching formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(DispatchingFormatter([ TaskFormatter(), DefaultFormatter() ]))
    log.addHandler(handler)

    # Task handler
    handler = TaskHandler()
    handler.setFormatter(TaskFormatter())
    log.addHandler(handler)

    log.info('Starting test')

    tr = ProccessMethod.getTranslations()
    print tr

    class Manager:
        def remove():
            pass

    SickbeardWorker.tasklog = Tasklog()
    SickbeardWorker.manager = Manager()
    SickbeardWorker.config  = {
        'ssl'        : False,
        'host'       : 'localhost',
        'port'       : 8081,
        'username'   : 'admin',
        'password'   : 'admin',
        'method'     : ProccessMethod.DEFAULT,
        'quiet'      : True,
        'force'      : False,
        'priority'   : False,
        'remove'     : False,
        'remove_data': False,
        'workers'    : 4
    }

    num_workers = SickbeardWorker.config['workers']
    wqueue      = SickbeardWorkerQueue(num_workers = num_workers, log_status = True, log_interval = 1)

    n = 0
    #reactor.callLater(0, wqueue.put, "some job" + str(n ++ 1))
    #reactor.callLater(1, wqueue.put, "some job" + str(n ++ 1))
    #reactor.callLater(random.random() * 10, wqueue.put, "some job" + str(n ++ 1))
    #reactor.callLater(random.random() * 10, wqueue.put, "some job" + str(n ++ 1))
    #reactor.callLater(random.random() * 10, wqueue.put, "some job" + str(n ++ 1))
    #reactor.callLater(random.random() * 10, wqueue.put, "some job" + str(n ++ 1))
    #reactor.callLater(random.random() * 10, wqueue.put, "some job" + str(n ++ 1))
    #reactor.callLater(random.random() * 10, wqueue.put, "some job" + str(n ++ 1))

    reactor.callLater(0, wqueue.put, Task(Torrent()))

    reactor.run()
