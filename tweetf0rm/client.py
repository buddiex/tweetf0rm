import logging
import os

import click
# import sys, time, argparse, random, copy, pprint
# sys.path.append(".")
from tweetf0rm.redis_helper import NodeQueue, NodeCoordinator
from tweetf0rm.utils import node_id, hash_cmd
# from tweetf0rm.exceptions import NotImplemented
import config
# from tweetf0rm.handler.oracle_handler import OracleHandler
# from tweetf0rm.twitterapi.twitter_api import TwitterAPI
# import json, os
from server import main

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s-[%(module)s][%(funcName)s]: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)



def send_to_server(ctx, cmd, in_cmd):
    cmd['cmd_hash'] = hash_cmd({'cmd': in_cmd})
    cmd['cmd'] = in_cmd
    ctx.obj['node_queue'].put(cmd)
    logger.info('sending {}'.format(cmd))
    ctx.obj['node_queue'].put(cmd)


# pp = pprint.PrettyPrinter(indent=4)

 # default='ids',type=click.Choice(['ids', 'users']), help='the tweet id that you want to fetch')

args_dict = {
    'user_id':{
        'args': ['-uid','--user-id'],
        'kwargs':{'required':True,
                  'help': 'the user id that you want to crawl his/her friends (who he/she is following) or followers'
                  }
                },

     'tweet_id':{
        'args': ['-tid','--tweet-id'],
        'kwargs':{'required':True,
                  'help': 'the tweet id that you want to fetch'
                  }
                },

    'data_type':{
        'args': ['-dt','--data-type'],
        'kwargs':{'default': 'users',
                  'help': '"ids" or "users" (default to ids) what the results are going to look like (either a list of twitter user ids or a list of user objects)',
                  'type': click.Choice(['ids', 'users'])
                  }
                },
    'depth':{
        'args': ['-d','--dept'],
        'kwargs':{'default': 1,
                  'help': 'the depth of the network; e.g., if it is 2, it will give you his/her (indicated by the -uid) friends\' friends'
                  }
                }
    ,
    'batch_file':{
        'args': ['-f','--batch-file'],
        'kwargs':{'required':True,
                  'default': 1,
                  'help':"the location of the json file that has a list of user_ids or screen_names"

                  }
                }
       ,
    'output_file':{
        'args': ['-o','--output-file'],
        'kwargs':{'default': 'user_ids.json',
                  'help':"the location of the output json file for storing user_ids defualts to user.json"
                  }
                }
           ,
    'node_id':{
        'args': ['-nid','--node-id'],
        'kwargs':{
                  'help':"the node_id you want to interact with  default to the current machine",
                  'default':node_id()
                  }
                }
               ,
    'query':{
        'args': ['-q','--query'],
        'kwargs':{'default': None,
                  'help':"the search query"
                  }
                }
    }



"""@click.option(*args_dict['user_id']['args'], **args_dict['user_id']['kwargs'])
@click.option(*args_dict['data_type']['args'], **args_dict['data_type']['kwargs'])
@click.option(*args_dict['batch_file']['args'], **args_dict['batch_file']['kwargs'])
@click.option(*args_dict['output_file']['args'], **args_dict['output_file']['kwargs'])
@click.option(*args_dict['node_id']['args'], **args_dict['node_id']['kwargs'])
@click.option(*args_dict['tweet_id']['args'], **args_dict['tweet_id']['kwargs'])
@click.option(*args_dict['depth']['args'], **args_dict['depth']['kwargs'])
@click.option(*args_dict['query']['args'], **args_dict['query']['kwargs'])
@click.pass_context"""

@click.group()
@click.option('-v','--verbose', default=False, type=bool)
@click.option(*args_dict['node_id']['args'], **args_dict['node_id']['kwargs'])
@click.version_option('1.0')
@click.pass_context
def cli(ctx, verbose, node_id):
    """This  is a command line client for the social media analytics app.
        It works with commands listed.
        for more info about any command use:
            client_old.py command --help
    """
    nid = node_id

    # logger.info("node_id: %s"%(nid))
    node_queue = NodeQueue(nid, redis_config=config.conf['redis_config'])
    node_coordinator = NodeCoordinator(config.conf['redis_config'])
    ctx.obj['verbose'] = verbose
    ctx.obj['node_queue'] = node_queue
    ctx.obj['node_coordinator'] = node_coordinator


@cli.command()
@click.option("-a","--action", type = click.Choice(['start', 'stop', 'restart']))
@click.pass_context
def server(ctx,action):
    """Get a user's twitter followers"""
    logfile = os.path.join(os.getcwd(), "smapp.log")
    pidfile = os.path.join(os.getcwd(), "server.pid")

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    server = main(pidfile=pidfile)

    if action == "start":

        server.start()

    elif action == "stop":

        server.stop()

    elif action == "restart":

        server.restart()



@cli.command()
@click.option(*args_dict['user_id']['args'], **args_dict['user_id']['kwargs'])
@click.option(*args_dict['data_type']['args'], **args_dict['data_type']['kwargs'])
@click.option(*args_dict['batch_file']['args'], **args_dict['batch_file']['kwargs'])
@click.option(*args_dict['output_file']['args'], **args_dict['output_file']['kwargs'])
@click.option(*args_dict['tweet_id']['args'], **args_dict['tweet_id']['kwargs'])
@click.option(*args_dict['depth']['args'], **args_dict['depth']['kwargs'])
@click.option(*args_dict['query']['args'], **args_dict['query']['kwargs'])
@click.pass_context
def crawl_friends(ctx, user_id,data_type, depth):
    """Get a user's twitter friends"""

@cli.command()
@click.option(*args_dict['user_id']['args'], **args_dict['user_id']['kwargs'])
@click.option(*args_dict['data_type']['args'], **args_dict['data_type']['kwargs'])
@click.option(*args_dict['batch_file']['args'], **args_dict['batch_file']['kwargs'])
@click.option(*args_dict['output_file']['args'], **args_dict['output_file']['kwargs'])
@click.option(*args_dict['node_id']['args'], **args_dict['node_id']['kwargs'])
@click.option(*args_dict['tweet_id']['args'], **args_dict['tweet_id']['kwargs'])
@click.option(*args_dict['depth']['args'], **args_dict['depth']['kwargs'])
@click.option(*args_dict['query']['args'], **args_dict['query']['kwargs'])
@click.pass_context
def batch_crawl_friends(ctx,query):
    """get multiple user friends"""


@cli.command()
@click.option(*args_dict['user_id']['args'], **args_dict['user_id']['kwargs'])
@click.option(*args_dict['data_type']['args'], **args_dict['data_type']['kwargs'])
@click.option(*args_dict['node_id']['args'], **args_dict['node_id']['kwargs'])
@click.option(*args_dict['depth']['args'], **args_dict['depth']['kwargs'])
@click.pass_context
def crawl_followers(ctx,**kwargs):
    """Get a user's twitter followers"""
    in_cmd = click.get_current_context().info_name.upper()
    send_to_server(ctx,kwargs,in_cmd)

@cli.command()
@click.option(*args_dict['user_id']['args'], **args_dict['user_id']['kwargs'])
@click.option(*args_dict['data_type']['args'], **args_dict['data_type']['kwargs'])
@click.option(*args_dict['batch_file']['args'], **args_dict['batch_file']['kwargs'])
@click.option(*args_dict['output_file']['args'], **args_dict['output_file']['kwargs'])
@click.option(*args_dict['node_id']['args'], **args_dict['node_id']['kwargs'])
@click.option(*args_dict['tweet_id']['args'], **args_dict['tweet_id']['kwargs'])
@click.option(*args_dict['depth']['args'], **args_dict['depth']['kwargs'])
@click.option(*args_dict['query']['args'], **args_dict['query']['kwargs'])
@click.pass_context
def batch_crawl_followers():
    """get multiple user followers"""

@cli.command()
@click.option(*args_dict['user_id']['args'], **args_dict['user_id']['kwargs'])
@click.pass_context
def crawl_user_timeline(ctx,**kwargs):
    """get timeline of one users"""
    in_cmd = click.get_current_context().info_name.upper()
    send_to_server(ctx, kwargs, in_cmd)

@cli.command()
@click.option(*args_dict['batch_file']['args'], **args_dict['batch_file']['kwargs'])
@click.option(*args_dict['output_file']['args'], **args_dict['output_file']['kwargs'])
@click.pass_context
def batch_crawl_user_timeliness(ctx,**kwargs):
    """get timeline of multiple users"""
    in_cmd = click.get_current_context().info_name.upper()

    if kwargs['batch_file']:
     if not os.path.exists(kwargs['batch_file']):
         raise Exception("doesn't exist... ")
     with open(os.path.abspath(kwargs['batch_file']), 'rb') as f:
          users_list = (id for id in f)
    n = 0
    for user_id in users_list:
        kwargs['user_id'] = user_id
        send_to_server(ctx, kwargs, in_cmd)
        if n == 1000:
            logger.warn("sent {} files".format(n))
            break
        n +=1



# @cli.command()
# def batch_crawl_tweet():
#     """Command on cmd2"""


# @cli.command()
# def get_user_id_from_screen_names():
#     """Command on cmd2"""
#
# @cli.command()
# def get_users_from_ids():
#     """not implemented"""

# @cli.command()
# def list_nodes():
#     """not implemented"""
#
# @cli.command()
# def node_qsize():
#     """not implemented"""
#
# @cli.command()
# def clear_node_queues():
#     """not implemented"""
#
# @cli.command()
# def search():
#     """not implemented"""

# cli = click.CommandCollection(sources=[cli1, cli2])
if __name__ == '__main__':
    cli(obj={})




























