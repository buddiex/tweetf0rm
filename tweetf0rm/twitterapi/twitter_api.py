#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Users.py: all user related farming; friends, followers, user objects; etc.
You can use this raw class, but normally you will use a script in the scripts folder
'''

import logging

logger = logging.getLogger(__name__)

import twython, tweepy
import json, time
from tweetf0rm.exceptions import MissingArgs, MaxRetryReached
from tweetf0rm.utils import md5, full_stack

MAX_RETRY_CNT = 5
SAVE_THRESHOLD = 400

class TwitterAPI():

    def __init__(self, write_to_handlers=[],*args, **kwargs ):
        """
        Constructor with apikeys, and output folder
        * apikeys: apikeys
        """
        import copy
        self.apikeys = copy.copy(kwargs.pop('apikeys', None))
        
        if not self.apikeys:
            raise MissingArgs('apikeys is missing')
        auth = tweepy.OAuthHandler(self.apikeys['app_key'], self.apikeys['app_secret'])
        auth.set_access_token(self.apikeys['oauth_token'], self.apikeys['oauth_token_secret'])
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, *args, **kwargs)

        self.write_to_handlers = write_to_handlers

    def update_handlers(self, items, bucket, user_id, cmd_handlers=[]):
        if len(items)>0:
            for handler in self.write_to_handlers:
                handler.append(items, bucket=bucket, key=user_id)
            for handler in cmd_handlers:
                handler.append(items, bucket=bucket, key=user_id)

    def find_all_followers(self, user_id=None, cmd_handlers=[], bucket="followers"):
        
        if not user_id:
            raise MissingArgs("user_id cannot be None")

        retry_cnt = MAX_RETRY_CNT
        cnt, cnt2 = 0, 0
        try:
            #get the ids of the followers then get the user object from ids
            for followers_id in tweepy.Cursor(self.api.followers_ids, screen_name=user_id).pages():
                cnt += len(followers_id)
                logger.info("followers id gotten {}-- total {}".format(len(followers_id), cnt))
                pos = 0
                screen_names_list = []
                while pos + 100 <= len(followers_id):
                    batch_followers = self.api.lookup_users(user_ids=followers_id[pos:pos+100])
                    cnt2 += len(batch_followers)
                    batch_followers_list = [bf._json for bf in batch_followers]
                    screen_names_list.extend([bf['screen_name'] for bf in batch_followers_list])
                    logger.info("{} followers".format(cnt2))
                    self.update_handlers(batch_followers_list, bucket, user_id, cmd_handlers)
                    pos += 100
                self.update_handlers(screen_names_list, 'follower_ids', user_id, cmd_handlers)
                time.sleep(1)
        except Exception as exc:
            logger.debug("exception: %s" % exc)
            logger.debug(full_stack())
            time.sleep(10)
            retry_cnt -= 1
            if retry_cnt == 0:
                raise MaxRetryReached("max retry reached due to %s" % exc)
            raise
                
        logger.debug("finished find_all_followers for %s..." % user_id)
        
    def find_all_follower_ids(self, user_id=None,bucket = "follower_ids", cmd_handlers = []):

        if (not user_id):
            raise MissingArgs("user_id cannot be None")

        retry_cnt = MAX_RETRY_CNT
        cnt = 0
        try:
            for follower_ids in tweepy.Cursor(self.api.followers_ids, screen_name=user_id).pages():
                cnt += len(follower_ids)
                self.update_handlers(follower_ids, bucket, user_id, cmd_handlers)                 
                logger.debug(" {} followers... and {} so far... now sleeping for 10sec".format(len(follower_ids),cnt))
                time.sleep(10)

        except Exception as exc:
            import traceback
            time.sleep(5)
            logger.error("exception: from here %s"% exc)
            retry_cnt -= 1
            if (retry_cnt == 0):
                logger.error("ending due to %s"%(exc))
                raise MaxRetryReached("max retry reached due to %s"%(exc))
            traceback.print_exc()

        logger.debug("finished find_all_follower_ids for %s..."%(user_id))


    def find_all_friends(self, user_id=None, write_to_handlers=[], cmd_handlers=[], bucket="friends"):

        if (not user_id):
            raise MissingArgs("user_id cannot be None")

        retry_cnt = MAX_RETRY_CNT
        cursor = -1
        while cursor != 0 and retry_cnt > 1:
            try:
                friends = self.get_friends_list(user_id=user_id, cursor=cursor, count=200)

                for handler in write_to_handlers:
                    handler.append(json.dumps(friends), bucket=bucket, key=user_id)

                for handler in cmd_handlers:
                    handler.append(json.dumps(friends), bucket=bucket, key=user_id) 

                cursor = int(friends['next_cursor'])

                logger.debug("find #%d friends... NEXT_CURSOR: %d"%(len(friends["users"]), cursor))

                time.sleep(2)
            except twython.exceptions.TwythonRateLimitError:
                self.rate_limit_error_occured('friends', '/friends/list')
            except Exception as exc:
                time.sleep(10)
                logger.debug("exception: %s"%exc)
                retry_cnt -= 1
                if (retry_cnt == 0):
                    raise MaxRetryReached("max retry reached due to %s"%(exc))

        logger.debug("finished find_all_friends for %s..."%(user_id))


    def find_all_friend_ids(self, user_id=None, write_to_handlers=[], cmd_handlers=[], bucket="friend_ids"):

        if (not user_id):
            raise MissingArgs("user_id cannot be None")

        retry_cnt = MAX_RETRY_CNT
        cursor = -1
        while cursor != 0 and retry_cnt > 1:
            try:
                friend_ids = self.get_friends_ids(user_id=user_id, cursor=cursor, count=200)

                for handler in write_to_handlers:
                    handler.append(json.dumps(friend_ids), bucket=bucket, key=user_id) 

                for handler in cmd_handlers:
                    handler.append(json.dumps(friend_ids), bucket=bucket, key=user_id) 

                cursor = int(friend_ids['next_cursor'])

                logger.debug("find #%d friend_ids... NEXT_CURSOR: %d"%(len(friend_ids["ids"]), cursor))

                time.sleep(2)
            except twython.exceptions.TwythonRateLimitError:
                self.rate_limit_error_occured('friends', '/friends/ids')
            except Exception as exc:
                time.sleep(10)
                logger.debug("exception: %s"%exc)
                retry_cnt -= 1
                if (retry_cnt == 0):
                    raise MaxRetryReached("max retry reached due to %s"%(exc))

        logger.debug("finished find_all_friend_ids for %s..."%(user_id))


    def fetch_user_timeline(self, user_id=None, write_to_handlers=[], cmd_handlers=[], bucket="timelines"):

        if not user_id:
            raise Exception("user_timeline: user_id cannot be None")

        cnt = 0
        retry_cnt = MAX_RETRY_CNT
        timeline = []
        try:
            for statuses in tweepy.Cursor(self.api.user_timeline, id=user_id).pages():
                cnt += len(statuses)
                for tweet in statuses:
                    timeline.append(tweet._json)
                logger.info("...{} tweets downloaded for {}".format(cnt, user_id))
            time.sleep(1)

        except Exception as exc:
            time.sleep(10)
            logger.debug("exception: {}".format(exc))
            retry_cnt -= 1
            if retry_cnt == 0:
                raise MaxRetryReached("max retry reached due to {}".format(exc))

        self.update_handlers(timeline, bucket, user_id, cmd_handlers)
        logger.info("done for [%s] total tweets: %d "%(user_id, cnt))

    def fetch_tweet_by_id(self, tweet_id = None, write_to_handlers=[], cmd_handlers=[], bucket="tweets"):

        if not tweet_id:
            raise Exception("show_status: tweet_id cannot be None")
        tweet = None
        retry_cnt = MAX_RETRY_CNT
        while retry_cnt > 1:
            try:
                tweet = self.show_status(id=tweet_id)

                # logger.debug('%d > %d ? %s'%(prev_max_id, current_max_id, bool(prev_max_id > current_max_id)))
                logger.info("Fetched tweet [%s]" % (tweet_id))

                break

            except twython.exceptions.TwythonRateLimitError:
                self.rate_limit_error_occured('statuses', '/statuses/show')
            except twython.exceptions.TwythonError as te:
                if ( te.error_code == 404 or te.error_code == 403 ):
                    logger.info("Tweet [%s] unavailable. Error code: %d" % (tweet_id, te.error_code))

                    break
                else:
                    time.sleep(10)
                    logger.error("exception: %s"%(te))
                    retry_cnt -= 1
                    if (retry_cnt == 0):
                        raise MaxRetryReached("max retry reached due to %s"%(te))
            except Exception as exc:
                time.sleep(10)
                logger.error("exception: %s, %s"%(exc, type(exc)))
                retry_cnt -= 1
                if (retry_cnt == 0):
                    raise MaxRetryReached("max retry reached due to %s"%(exc))

        if (tweet != None):
            for handler in write_to_handlers:
                handler.append(json.dumps(tweet), bucket=bucket, key="tweetList")
        else:
            for handler in write_to_handlers:
                handler.append(json.dumps({"id":tweet_id}), bucket=bucket, key="tweetList")

        logger.debug("[%s] tweet fetched..." % tweet_id)


    def get_user_ids_by_screen_names(self, seeds):
        #get user id first
        screen_names = list(set(seeds))
        user_ids = set()		

        if len(screen_names) > 0:
            users = self.lookup_user(screen_name=screen_names)

            for user in users:
                user_ids.add(user['id'])

        return user_ids

    def get_users(self, seeds):
        #get user id first
        user_ids = list(set(seeds))
        users = set()
    

        if len(user_ids) > 0:
            users = self.lookup_user(user_id=user_ids)

        return users

    def search_by_query(self, query = None, geocode=None, lang=None, key=None, write_to_handlers=[], cmd_handlers=[], bucket="tweets"):

        if not query:
            raise Exception("search: query cannot be None")

        if not key:
            key = md5(query)

        logger.info("received query: %s "%(query))

        prev_max_id = -1
        current_max_id = 0
        last_lowest_id = current_max_id # used to workaround users who has less than 200 tweets, 1 loop is enough...
        cnt = 0
        
        retry_cnt = MAX_RETRY_CNT
        result_tweets = []
        while current_max_id != prev_max_id and retry_cnt > 1:
            try:
                if current_max_id > 0:
                    tweets = self.search(q=query, geocode=geocode, lang=lang, max_id=current_max_id-1, count=100)
                else:
                    tweets = self.search(q=query, geocode=geocode, lang=lang, count=100)

                prev_max_id = current_max_id # if no new tweets are found, the prev_max_id will be the same as current_max_id
                result_tweets = tweets['statuses']
                for tweet in result_tweets:
                    if current_max_id == 0 or current_max_id > long(tweet['id']):
                        current_max_id = long(tweet['id'])

                #no new tweets found
                if (prev_max_id == current_max_id):
                    break;
                
                cnt += len(result_tweets)
                logger.debug('{} tweets gotten so far'.format(cnt))

                for tweet in result_tweets:
                    for handler in write_to_handlers:
                        handler.append(json.dumps(tweet), bucket=bucket, key=key)

                    for handler in cmd_handlers:
                        handler.append(json.dumps(tweet), bucket=bucket, key=key)
                #logger.info(cnt)

                # logger.debug('%d > %d ? %s'%(prev_max_id, current_max_id, bool(prev_max_id > current_max_id)))

                time.sleep(1)

            except twython.exceptions.TwythonRateLimitError:
                self.rate_limit_error_occured('search', '/search/tweets')
            except Exception as exc:
                time.sleep(10)
                logger.debug("exception: %s"%exc)
                retry_cnt -= 1
                if (retry_cnt == 0):
                    raise MaxRetryReached("max retry reached due to %s"%(exc))

        if (len(result_tweets) > 0):
            for tweet in result_tweets:
                for handler in write_to_handlers:
                    handler.append(json.dumps(tweet), bucket=bucket, key=key)

                for handler in cmd_handlers:
                    handler.append(json.dumps(tweet), bucket=bucket, key=key)
        else:
            for handler in write_to_handlers:
                handler.append(json.dumps({}), bucket=bucket, key=key)

        logger.info("[%s] total tweets: %d "%(query, cnt))