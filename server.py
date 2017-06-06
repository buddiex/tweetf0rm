#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import pprint
import sys
import time
from daemons  import daemonizer
from daemons.prefab import run
import config
from tweetf0rm.redis_helper import NodeQueue
from tweetf0rm.scheduler import Scheduler
from tweetf0rm.utils import full_stack, node_id, check_config, archive

logger = logging.getLogger(__name__)


sys.path.append(".")


def start_server(config, proxies):
    import copy
    check_config(config)
    config = copy.copy(config)
    this_node_id = node_id()
    node_queue = NodeQueue(this_node_id, redis_config=config['redis_config'])
    node_queue.clear()
    scheduler = Scheduler(this_node_id, config=config, proxies=proxies)
    # node_coordinator = NodeCoordinator(config['redis_config'])
    # node_coordinator.clear()

    # the main event loop, actually we don't need one, since we can just join on the crawlers and don't stop
    # until a terminate command is issued to each crawler;
    # but we need one to report the status of each crawler and perform the tarball tashs...
    last_archive_ts = time.time() + 3600  # the first archive event starts 2 hrs later...
    pre_time = time.time()
    print ('here')
    last_load_balancing_task_ts = time.time()
    logger.info('starting node_id: %s' % this_node_id)
    while True:
        if time.time() - pre_time > 120:
            logger.info(pprint.pformat(scheduler.crawler_status()))
            pre_time = time.time()
            if scheduler.is_alive():
                cmd = {'cmd': 'CRAWLER_FLUSH'}
                scheduler.enqueue(cmd)

        if time.time() - last_archive_ts > 3600:
            archive()
            last_archive_ts = time.time()

        if not scheduler.is_alive():
            logger.info("no crawler is alive... waiting to recreate all crawlers...")
            time.sleep(120)  # sleep for a minute and retry
            continue

        if time.time() - last_load_balancing_task_ts > 1800:  # try to balance the local queues every 30 mins
            logger.info("balancing queues")
            last_load_balancing_task_ts = time.time()
            cmd = {'cmd': 'BALANCING_LOAD'}
            scheduler.enqueue(cmd)

        logger.info("waiting for commands from client...")
        cmd = node_queue.get(block=True, timeout=360)

        if cmd:
            scheduler.enqueue(cmd)

# @daemonizer.run(pidfile="/tmp/sleepy.pid")
def main():

    conf = config.conf
    proxies = None
    if config.proxies:
        with open(config.proxies, 'rb') as proxy_f:
            proxies = json.load(proxy_f)['proxies']

    try:
        start_server(conf, proxies)
        print ('started')
    except KeyboardInterrupt:
        logger.error('You pressed Ctrl+C!')
        pass
    except Exception as exc:
        logger.error(exc)
        logger.error(full_stack())
    finally:
        pass


class run_main(run.RunDaemon):
    def run(self):
        main()


if __name__ == "__main__":

    # class main3(run.RunDaemon):
    #
    #     def run(self):
    #
    #         while True:
    #
    #             time.sleep(3)
    #             print ('test3')
    #             logger.info('testlogger')

    # action = sys.argv[1]
    main()

    # # logfile = os.path.join(os.getcwd(), "smapp.log")
    # pidfile = os.path.join(os.getcwd(), "sleepy.pid")
    #
    # logging.basicConfig(filename=logfile, level=logging.DEBUG)
    #
    # server = run_main(pidfile = pidfile)
    #
    # if action == "start":
    #     server.start()
    #     print("stated")
    #
    # elif action == "stop":
    #     server.stop()
    #
    # elif action == "restart":
    #     server.restart()

 # python2.7 server.py stop