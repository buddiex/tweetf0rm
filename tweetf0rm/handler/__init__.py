from .inmemory_handler import InMemoryHandler
from .file_handler import FileHandler
from .oracle_handler import OracleHandler
import tweetf0rm.handler
import copy

__all__ = ["InMemoryHandler", "FileHandler", "OracleHandler"]
avaliable_handlers = copy.copy(__all__)


def create_handler(handler_config=None):
    # inmemory_handler_config = {
    # 	"name": "InMemoryHandler",
    # 	"args": {
    # 		"verbose": True
    # 	}
    # }
    cls = getattr(tweetf0rm.handler, handler_config["name"])
    return cls(**handler_config["args"])


def create_handlers(handler_configs=None):
    handlers = []
    for k, v in handler_configs.items():
        if v['active']:
            handlers.append(create_handler(v))
    return handlers
