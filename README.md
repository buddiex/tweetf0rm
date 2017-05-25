
tweetf0rm
=========

A crawler that helps you collect data from Twitter for research. Most of the heavy works are already done by [Twython](https://github.com/ryanmcgrath/twython). ``tweetf0rm`` is just a collection of python scripts help to deal with parallelization, proxies, and errors such as connection failures. In most use cases, it will auto-restart when an exception occurs. And, when a crawler exceeds the Twitter API's [rate limit](https://dev.twitter.com/docs/rate-limiting/1.1/limits), the crawler will pause itself and auto-restart later.

To workaround Twitter's rate limits, ``tweetf0rm`` can spawn multiple crawlers each with different proxy and twitter dev account on a single computer (or on multiple computers) and collaboratively ``farm`` user tweets and twitter relationship networks (i.e., friends and followers). The communication channel for coordinating among multiple crawlers is built on top of [redis](http://redis.io/) -- a high performance in-memory key-value store. It has its own scheduler that can balance the load of each worker (or worker machines).

It's quite stable for the things that I want to do. I have collected billions of tweets from **2.6 millions** twitter users in about 2 weeks with a single machine.
