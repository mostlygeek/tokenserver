import os
import json
import time
import signal
import base64
import sys
import threading

from pyramid.threadlocal import get_current_registry

from vep.verifiers.local import LocalVerifier
from vep.jwt import JWT

from zope.interface import implements, Interface

from powerhose.jobrunner import JobRunner
from powerhose.client.workers import Workers
from powerhose import logger


class IPowerhoseRunner(Interface):

    def execute(*args, **kw):
        """ """

# global registry
# # XXX thread-safetiness ?

# XXX see https://github.com/Pylons/pyramid/issues/442
def bye(*args, **kw):
    stop_runners()
    sys.exit(1)

signal.signal(signal.SIGTERM, bye)
signal.signal(signal.SIGINT, bye)

_runners = {}
_workers = {}


def stop_runners():
    logger.debug("stop_runner starts")

    for workers in _workers.values():
        workers.stop()

    logger.debug("workers killed")

    for runner in _runners.values():
        logger.debug('Stopping powerhose master')
        runner.stop()

    logger.debug("stop_runner ends")


class CryptoWorkers(threading.Thread):
    def __init__(self, workers_cmd, num_workers):
        threading.Thread.__init__(self)
        self.workers = Workers(workers_cmd, num_workers=num_workers)

    def run(self):
        logger.debug('Starting powerhose workers')
        self.workers.run()

    def stop(self):
        logger.debug('Stopping powerhose workers')
        self.workers.stop()
        self.join()


class PowerHoseRunner(object):
    implements(IPowerhoseRunner)

    def __init__(self, endpoint, workers_cmd, num_workers=5, **kw):
        self.endpoint = endpoint
        self.workers_cmd = workers_cmd
        if self.endpoint not in _runners:
            _runners[self.endpoint] = JobRunner(self.endpoint)
            _workers[self.endpoint] = CryptoWorkers(self.workers_cmd,
                                                    num_workers=num_workers)
        self.runner = _runners[self.endpoint]
        logger.debug('Starting powerhose master')
        self.runner.start()
        time.sleep(.5)
        self.workers = _workers[self.endpoint]
        self.workers.start()

    def execute(self, *args, **kw):
        return self.runner.execute(*args, **kw)