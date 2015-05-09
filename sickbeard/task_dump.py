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

import task
import tasklog
import logging
import sys

if __name__=="__main__":

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    log = logging.getLogger('test')
    log.info('Starting test')

    tasklog = tasklog.Tasklog()

    #print len(tasklog.d)

    # Re-map modules for pickle
    sys.modules['sickbeard.task'] = task

    #tasks = tasklog.get_all(deep_copy = False)
    tasks = tasklog.d

    for task in tasks.itervalues():
        #print str(id(task))  + "> " + str(vars(task))
        #for record in task.output:
        #    print str(id(record.task)) + "> " + str(vars(record))
        #    break

        #d = convert.todict(task)

        ts = task.torrent_info.status

        # task._completed_time = task.completed_time
        # task._torrent_info   = task.torrent_info
        # task._status         = task.status
        # task._failed         = task.failed

        log.info("%s: %s / %s (%d)" % (task.id, task.status, ts["name"], len(task.output)) )

        # del task.completed_time
        # del task.torrent_info
        # del task.status
        # del task.failed

        #        log.info("> %s" % str(line) )
        #if not task.output is None:
        #    for line in task.output:
        #        log.info("> %s" % str(line) )

    tid = 'fbe7a706-59fd-45ad-b5dc-39f1275cbd28'
    log.info('Deleting: %s' % tid)
    tasklog.delete(tid)

