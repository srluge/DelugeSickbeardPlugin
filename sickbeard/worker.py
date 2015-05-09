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
import error

from twisted.internet       import reactor, defer, task
from twisted.internet.defer import inlineCallbacks, DeferredQueue

from abc                    import ABCMeta, abstractmethod

class Worker(object):
    """Abstract class for an active worker continously monitoring queue for new work"""

    __metaclass__ = ABCMeta

    workers = 0   # Counter instantiated workers
    tasks   = 0   # Counter picked up tasks

    def __init__(self, dqueue):
        self.id      = Worker.workers # Worker id
        self.task    = None           # Current task working on
        self.seq     = -1             # Last unique Task-ID worker is/was working on
        self.dqueue  = dqueue         # Queue to automatically fetch work from
        self.working = False          # Worker running or waiting for new task
        self.log     = logging.getLogger(type(self).__name__)

        Worker.workers = Worker.workers + 1

    @inlineCallbacks
    def run(self):
        """Worker loop"""
        while 1:
            # Wait for work from the queue. Defers / waits if there is no new
            # work.
            if not self.dqueue.has_new_work():
                self.working = False
                self.log.debug("worker %s: waiting for new task", self.id)

            self.task              = yield self.dqueue.get()
            self.working           = True
            self.dqueue.log_active = True

            if self.task is None:
                # kill all workers
                self.dqueue.put(None)
                return

            # Set task id
            self.seq = Worker.tasks
            Worker.tasks = Worker.tasks + 1

            # Do the work
            try:
                self.log.debug("worker %s, task %d: picked up task" % (self.id, self.seq))
                yield self.work(self.task)
            except Exception as e:
                for line in error.format_exception():
                   self.log.error("worker %s, task %d, : %s" % (self.id, self.seq, line))
            finally:
                self.log.debug("worker %s, task %s: completed" % (self.id, self.seq))
                self.task = None

    @abstractmethod
    def work(self, task):
        """
        Do work on task.

        Hint: Use yield in combination with @inlineCallbacks when
              tasks call blocking functions.
        """
        return

    def kill(self):
        """Kill all workers"""
        self.dqueue.put(None)

    def _sleep(self, secs):
        """Sleep helper function. To be called from method work() if needed."""
        d = defer.Deferred()
        reactor.callLater(secs, d.callback, None)
        return d

class WorkerQueue(DeferredQueue):
    """Event driven 'worker' queue to safely offload work to N workers"""

    _LOG_INTERVAL = 4

    def __init__(self, worker_class, num_workers, log_status = False, log_interval = _LOG_INTERVAL):

        super(WorkerQueue, self).__init__()

        if not self.log:
            self.log = logging.getLogger(type(self).__name__)

        self.num_workers  = num_workers   # Number of workers to start
        self.workers      = []            # List with spawned workers
        self.log_active   = True          # Next log interval print a status message
        self.running      = False         # All workers are setup and running/waiting
        self.worker_class = worker_class  # Worker class to instantiate

        if not issubclass(self.worker_class, Worker):
            raise TypeError("%s not subclass of Worker" % (self.worker_class))

        if log_status:
            self.log_status
            l = task.LoopingCall(self.log_status)
            l.start(log_interval)


        self.spawn_workers()
        self.running = True

    def spawn_workers(self):
        for n in range(self.num_workers):
            worker = self.worker_class(self)
            self.log.info("Spawning worker %d" % n)
            self.workers.append(worker)

            # Start worker. Note that the Worker will immediately deferre
            # since there is no work available in the queue.
            worker.run()

    def busy_workers(self):
        """Return number of active workers"""

        w = len(self.waiting)
        if self.running:
            b = self.num_workers - w
        else:
            b = 0

        return b

    def is_working(self):
        """Check if one or more workers are active"""
        return True if self.busy_workers > 0 else False

    def has_new_work(self):
        """Check if there is new work pending (which is not yet worked on by a worker)"""
        return True if len(self.pending) > 1 else False

    def log_status(self):
        p = len(self.pending)
        w = len(self.waiting)

        if self.running:
            b = self.num_workers - w
        else:
            b = 0

        # Only log if active work is being done or ready for pickup
        if p > 0 or b > 0:
            self.log_active = True

        if self.log_active:
            self.log.info("%d task(s) pending, %d worker(s) busy", p, b)

        if p == 0 and b == 0:
            self.log_active = False

    def get_all(self, pending_only = False):
        """
        Return dictionary containing a copy of pending/busy tasks. Indexed by
        task id. Task data is stored in the DeferredQueue in the pending
        list and in WorkerQueue in the spawned workers list.
        """

        # All currently pending tasks - convert list to dict
        taskq = dict((task.id, task) for task in self.pending)

        # Tasks picked up and worked on - convert list to dict
        if not pending_only:
            for worker in self.workers:
                if worker.working:
                    task = worker.task
                    taskq[task.id] = task

        return taskq
