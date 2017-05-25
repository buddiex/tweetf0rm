import click

# @click.group()
# @click.option('--debug/--no-debug', default=False)
# @click.pass_context
# def cli(ctx, debug):
#     ctx.obj['DEBUG'] = debug

# @cli.command()
# @cli.argument
# @click.pass_context
# def sync(ctx):
#     """Command on cli1"""
#     click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))

# if __name__ == '__main__':
#     cli(obj={})



# @click.group()
# @click.argument('filename')
# @click.argument('config')
# @click.argument('src', nargs=-1)
# @click.argument('dst', nargs=1)
# @click.option('--check_proxies', is_flag=True) 
# @click.pass_context
# def cli(ctx, config, filename, check_proxies):
#     ctx.obj['config'] = config

# @cli.command()
# @click.pass_context
# def cmd1(ctx):
#     """Command on cli1 --id asdfsf """
#     print ("asdf" + ctx.obj['config'])

# @cli.command()
# def cmd2():
#     """Command on cli21"""

# @cli.command()
# def cmd3():
#     """Command on cli22"""    

# # cli = click.CommandCollection(sources=[cli2])
# if __name__ == '__main__':
#     cli(obj={})

#
# import twython
# import tweepy
# import time
#
#
# conf = 	{"apikeys": {
#         "i0mf0rmer01" :{
#             "app_key":"zXR2BFtRreCMX3XzLbJUVRQLz",
#             "app_secret":"3nAN9aWljxxNP7xvZrnC4ci1wuynVTKVARvLec24LnbDNPMdDM",
#             "oauth_token":"2342906806-rnVpZYSxnvedx7TdTOpcVzyer7J1tiUtescGnMF",
#             "oauth_token_secret":"KBxmwFAhE5gACR8K4fvXW2MNQztBvIHgGClEiDEsarLFw"
#         }
#         }}
# apikeys = conf['apikeys']['i0mf0rmer01']
# consumer_key, consumer_secret =  apikeys['app_key'], apikeys['app_secret']
# access_token, access_token_secret = apikeys['oauth_token'], apikeys['oauth_token_secret']
#
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
# api = tweepy.API(auth)
#
# class TwitterAPI():
#
#     def __init__(self, *args, **kwargs):
#         """
#         Constructor with apikeys, and output folder
#         * apikeys: apikeys
#         """
#         # logger.info(kwargs)
#         import copy
#         self.apikeys = copy.copy(kwargs.pop('apikeys', None))
#
#         # if not apikeys:
#         #     raise MissingArgs('apikeys is missing')
#         auth = tweepy.OAuthHandler(self.apikeys['app_key'], self.apikeys['app_secret'])
#         auth.set_access_token(self.apikeys['oauth_token'], self.apikeys['oauth_token_secret'] )
#         self.api = tweepy.API(auth,*args, **kwargs )
#
#     def get_followers(self):
#         for page in tweepy.Cursor(self.api.followers_ids, screen_name="gtbank").pages():
#             import pdb; pdb.set_trace()
#             print(len(page))
#             time.sleep(1)
#
# twt = TwitterAPI(apikeys = conf['apikeys']['i0mf0rmer01'])
#
# twt.get_followers()
import pandas as pd
import json
import cx_Oracle
import config
from sqlalchemy import create_engine
data = 'data/followers/gtbank'

try:
  oraconn = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
except cx_Oracle.DatabaseError as exception:
  raise

db_eng = create_engine(config.SQLALCHEMY_DATABASE_URI, encoding='utf8')


def load_list(rows_list):
    df = pd.DataFrame(rows_list)
    df[['screen_name','id_str','description', 'created_at', 'default_profile',
'default_profile_image','statuses_count', 'favourites_count','followers_count',
'friends_count', 'listed_count','geo_enabled', 'lang','location', 'name', 'profile_background_image_url',
'profile_banner_url', 'profile_image_url', 'protected', 'time_zone',
'url', 'utc_offset', 'verified']].to_sql('data', db_eng, if_exists='append')

def get_chunked_json(chunksize):
    if db_eng.has_table('data'):
        db_eng.execute('drop table data')
    with open(data, "r") as fo:
        rows_list, cnt = [], 1
        for ln in fo:
            rows_list.append(json.loads(ln))
            if cnt % chunksize == 0:
                load_list(rows_list)
                rows_list=[]
                print('loaded {}'.format(cnt))
#             if cnt == 1000:
#                 break
            cnt +=1
        if rows_list:
            load_list(rows_list)
get_chunked_json(100000)
