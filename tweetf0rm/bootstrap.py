#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import pprint
import sys
import time

import config
from tweetf0rm import logger
from tweetf0rm.redis_helper import NodeQueue
from tweetf0rm.scheduler import Scheduler
from tweetf0rm.utils import full_stack, node_id, check_config, archive

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


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-c', '--config', help="config.json that contains a) twitter api keys; b) redis connection string;", required = True)
    # parser.add_argument('-p', '--proxies', help="the proxies.json file")
    # args = parser.parse_args()
    conf = config.conf
    proxies = None
    if config.proxies:
        with open(config.proxies, 'rb') as proxy_f:
            proxies = json.load(proxy_f)['proxies']

    try:
        start_server(conf, proxies)
    except KeyboardInterrupt:
        print()
        logger.error('You pressed Ctrl+C!')
        pass
    except Exception as exc:
        logger.error(exc)
        logger.error(full_stack())
    finally:
        pass


if __name__ == "__main__":
    main()
