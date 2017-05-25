#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tarfile
import time
import config
from tweetf0rm import logger
from concurrent import futures
from tweetf0rm.exceptions import InvalidConfig
import requests, json, traceback, sys
import hashlib





def check_config(config):
    if 'apikeys' not in config or 'redis_config' not in config:
        raise InvalidConfig('something is wrong with your config file... you have to have redis_config and apikeys')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_keys_by_min_value(qsizes):
    '''
    return a list of keys (crawler_ids) that have the minimum number of pending cmds
    '''

    min_v = min(qsizes.values())

    return [node_id for node_id in qsizes if qsizes[node_id] == min_v]


def full_stack():
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if not exc is None:  # i.e. if an exception is present
        del stack[-1]  # remove call of full_stack, the printed exception
        # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if not exc is None:
        stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr


def public_ip():
    r = requests.get('http://httpbin.org/ip')
    return r.json()['origin']


def md5(data):
    return hashlib.md5(data.encode("UTF-8")).hexdigest()


def hash_cmd(cmd):
    return md5(json.dumps(cmd))


def node_id():
    ip = public_ip()
    return md5(ip)


def archive():
    buckets = config.BUCKETS
    for bucket in buckets:
        folder = os.path.join(config.ARCHIVE_FOLDER, bucket)
        if not os.path.exists(folder):
            os.makedirs(folder)
    logger.info("start archive procedure...")

    with futures.ProcessPoolExecutor(max_workers=len(buckets)) as executor:
        future_proxies = {
            executor.submit(tarball_results,
                            os.path.join(config.OUT_FOLDER, bucket),
                            bucket,
                            os.path.join(config.ARCHIVE_FOLDER, bucket),
                            int(time.time()) - 3600): bucket
            for bucket in buckets
            }

        for future in future_proxies:
            future.add_done_callback(lambda f: logger.info("archive created? %s: [%s]" % f.result()))


def tarball_results(data_folder, bucket, output_tarball_foldler, timestamp):
    logger.info("archiving bucket: [%s] at %s" % (bucket, timestamp))

    if not os.path.exists(output_tarball_foldler):
        os.makedirs(output_tarball_foldler)

    gz_file = os.path.join(output_tarball_foldler, '%s.tar.gz' % timestamp)
    ll = []

    ignores = ['.DS_Store']
    for root, dirs, files in os.walk(data_folder):
        if len(files) > 0:
            with tarfile.open(gz_file, "w:gz") as tar:
                cnt = 0
                for f in files:
                    if f in ignores:
                        continue
                    f_abspath = os.path.join(root, f)
                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(f_abspath)

                    if mtime <= timestamp:
                        tar.add(f_abspath, '%s/%s' % (timestamp, f), recursive=False)
                        ll.append(f_abspath)
                        cnt += 1
                        if cnt % 1000 == 0:
                            logger.info("processed %d files" % (cnt))
                    else:
                        pass
                tar.close()

                for f in ll:
                    os.remove(f)

                return True, gz_file

    return False, gz_file


def format_proxy_list(proxy_list):
    rtn = []
    logger.warn('no proxy checking...')
    for proxies in proxy_list:
        for k,v in proxies.items():
        	rtn.append({'proxy_dict':{v:'{}://{}'.format(v,k)}, 'proxy':{k:v}})
    return rtn