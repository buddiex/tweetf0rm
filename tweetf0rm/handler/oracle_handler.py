#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
file_handler.py: handler that's collects the data, and write to the disk on a separate thread;
'''
import json
import cx_Oracle
import logging
from .base_handler import BaseHandler
import concurrent.futures as futures
from tweetf0rm.utils import full_stack
import config

logger = logging.getLogger(__name__)


def load_oracle(bucket, data, oraconn, sql):
    cursor = oraconn.cursor()
    cursor.prepare(sql)
    cursor.setinputsizes(cx_Oracle.CLOB)
    try:
        cursor.executemany(None, data)
        oraconn.commit()
    except cx_Oracle.Error as err:
        logger.debug("Error inserting into" + bucket + ": " + str(err))
        logger.error(full_stack())
        raise err

    logger.info(str(len(data)) + " items loaded to table " + bucket)
    return True


flush_size = {"tweets": 1000, "followers": 1000, "follower_ids": 4999, "friends": 1000, "friend_ids": 5000,
              "timelines": 1}


class DbHandler(BaseHandler):
    def __init__(self):
        super(DbHandler, self).__init__()
        try:
            self._conn = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD,
                                           dsn=config.ORACLE_DSN)
        except cx_Oracle.DatabaseError as exception:
            logger.debug('Failed to connect to %s\n', config['ORACLE_DSN'])
            logger.debug(exception)
            raise
        self._db_col = 'jd,created_time'
        for bucket in self.buckets:
            self.create_table(bucket)

    def create_table(self, tablename):
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = UPPER(:tbl_name)", tbl_name=tablename)
        result = cur.fetchall()
        # Table count returns 0, we need to create the table first
        if result[0][0] == 0:
            try:
                cols = self._db_col.split(',')
                sql = "create table {} ({} date, {} clob constraint {}_valid_json check ({} is json))".format(
                    tablename, cols[1], cols[0], tablename, cols[0])
                cur.execute(sql)
            except cx_Oracle.Error as err:
                logger.debug("Error creating table " + tablename + ": " + err.args[0].message)
                raise err
            else:
                logger.debug("New table created: " + tablename)

    def need_flush(self, bucket, key):
        cnt = len(self.buffer[bucket][key])
        logger.debug('flush size {}; bucket size {}'.format(flush_size[bucket], cnt))
        if cnt >= flush_size[bucket]:
            return True
        else:
            return False

    def flush(self, bucket):
        with futures.ProcessPoolExecutor(max_workers=3) as executor:
            for bucket, items in self.buffer.iteritems():
                if isinstance(items[0], int):
                    data_in = [(json.dumps(data, ensure_ascii=False).encode('utf-8'), None) for data in items]
                else:
                    data_in = [(json.dumps(data, ensure_ascii=False).encode('utf-8'), data['created_at']) for data in items]

                if len(items) > 0:
                    # send to a different process to operate and clear the buffer
                    sql = "INSERT INTO " + bucket + " (" + self._db_col + ") VALUES (:jd,:created_time)"
                    f = executor.submit(load_oracle, bucket, data_in, self.oraconn, sql)
                    self.clear(bucket)
        return True
