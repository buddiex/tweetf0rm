kill -9 `ps -ef | grep tweetf0rm | grep -v grep | awk '{print $2}'`
