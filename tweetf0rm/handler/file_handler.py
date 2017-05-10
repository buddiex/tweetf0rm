#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
file_handler.py: handler that's collects the data, and write to the disk on a separate thread;
'''
import os
import logging
import json
import config
from .base_handler import BaseHandler
import concurrent.futures as futures
from tweetf0rm.utils import full_stack

logger = logging.getLogger(__name__)


def flush_file(output_folder, bucket, items):
    try:
        bucket_folder = os.path.abspath('%s/%s' % (output_folder, bucket))

        for k, lines in items.iteritems():
            filename = os.path.abspath('%s/%s' % (bucket_folder, k))
            with open(filename, 'ab+') as outfile:
                for line in lines:
                    json.dump(line, outfile)
                    outfile.write('\n')

                # f.write('\n'.join(map(str, lines)))


            logger.info("flushed %d lines to %s" % (len(lines), filename))
    except:
        logger.error(full_stack())
    return True


flush_size = {"tweets": 1000, "followers": 1000, "follower_ids": 1000, "friends": 1000, "friend_ids": 1000,
              "timelines": 1}


class FileHandler(BaseHandler):
    def __init__(self, output_folder=config.OUT_FOLDER):
        super(FileHandler, self).__init__()
        self.output_folder = os.path.abspath(output_folder)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for bucket in self.buckets:
            bucket_folder = os.path.abspath('%s/%s' % (self.output_folder, bucket))
            if not os.path.exists(bucket_folder):
                os.makedirs(bucket_folder)

    def need_flush(self, bucket, key):
        cnt = len(self.buffer[bucket][key])
        logger.debug('flush size {}; bucket size {}'.format(flush_size[bucket], cnt))
        if cnt >= flush_size[bucket]:
            return True
        else:
            return False

    def flush(self, bucket):
        with futures.ProcessPoolExecutor(max_workers=3) as executor:
            # for each bucket it's a dict, where the key needs to be the file name;
            # and the value is a list of json encoded value
            for bucket, items in self.buffer.iteritems():
                if len(items) > 0:
                    # send to a different process to operate and clear the buffer
                    f = executor.submit(flush_file, self.output_folder, bucket, items)
                    self.clear(bucket)
        return True
