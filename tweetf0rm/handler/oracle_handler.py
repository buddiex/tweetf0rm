#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
file_handler.py: handler that's collects the data, and write to the disk on a separate thread;
'''
import json
import cx_Oracle
import dateutil.parser as dateparser
from tweetf0rm import logger
from .base_handler import BaseHandler
from .file_handler import FileHandler
import concurrent.futures as futures
from tweetf0rm.utils import full_stack
import config

try:
    ora_conn = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
except cx_Oracle.DatabaseError as exception:
    logger.debug('Failed to connect to %s\n', config.ORACLE_DSN)
    logger.debug(exception)
    raise


def load_oracle(bucket, data, sql):
    cursor = ora_conn.cursor()
    cursor.prepare(sql)
    cursor.setinputsizes(cx_Oracle.CLOB)
    try:
        cursor.executemany(None, data)
        ora_conn.commit()
    except cx_Oracle.Error as err:
        logger.debug("Error inserting into" + bucket + ": " + str(err))
        logger.error(full_stack())
        raise err

    logger.info(str(len(data)) + " items loaded to table " + bucket)
    return True


flush_size = {"tweets": 1000, "followers": 1000, "follower_ids": 4999, "friends": 1000, "friend_ids": 5000,
              "timelines": 1}


class OracleHandler(BaseHandler):
    def __init__(self):
        super(OracleHandler, self).__init__()
        try:
            self._conn = ora_conn
        except cx_Oracle.DatabaseError as exception:
            logger.debug('Failed to connect to %s\n', config['ORACLE_DSN'])
            logger.debug(exception)
            raise
        self._db_col = 'jd,created_time'
        for bucket in self.buckets:
            self.create_table(bucket)

    def table_exist(self, tablename):
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = UPPER(:tbl_name)", tbl_name=tablename)
        result = cur.fetchall()
        # Table count returns 0, we need to create the table first
        return result[0][0] > 0

    def create_table(self, tablename):

        if not self.table_exist(tablename):
            try:
                cur = self._conn.cursor()
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

        if cnt >= flush_size[bucket]:
            logger.debug('need to flush')
            return True
        else:
            return False

    def flush(self, bucket):
        for bucket, items in self.buffer.iteritems():
            if len(items) > 0:
                condition = bucket == 'follower_ids' or bucket == 'friend_ids'
                # save screen names in a file for use by the client
                if condition:
                    fhandler = FileHandler()
                    fhandler.flush(bucket)
                if not condition:
                    for key, values in items.iteritems():
                        data_in = [(json.dumps(data, ensure_ascii=False).encode('utf-8'), dateparser.parse(data['created_at'])) for data in values]
                        sql = "INSERT INTO " + bucket + " (" + self._db_col + ") VALUES (:jd,:created_time)"
                        with futures.ProcessPoolExecutor(max_workers=3) as executor:
                            f = executor.submit(load_oracle, bucket, data_in, sql)
            self.clear(bucket)
        return True

    def resultIter(self, cursor, array_size=1000):
        while True:
            results = cursor.fetchmany(array_size)
            if not results:
                break
            for result in results:
                yield result


    def query_db(self, sql, kwargs={}):
        cur = self._conn.cursor()
        cur.execute(sql, **kwargs)
        return self.resultIter(cur)

    def getUsers(self):
        cur = self._conn.cursor()
        cur.execute("select twt_handle from vw_twitter_user where TOTAL_TWEETS_COUNT <> 0")
        return [i[0] for i in self.resultIter(cur)]
