import os
from os.path import join, dirname, abspath
from dotenv import load_dotenv

basedir = dirname(__file__)
dotenv_path = join(basedir, '.env')
load_dotenv(dotenv_path)

OUT_FOLDER = "./data"
ARCHIVE_FOLDER = './data/archive'
proxies = join(basedir, 'scripts', 'proxies.json')
LOG_FILE = "smapp.log"
DB_NAME = "smdb"
TWITTER_HANDLE = 'gtbank'
ORACLE_USER = "analyse_usr"
ORACLE_PASSWORD = "Analytics!23"
ORACLE_DSN = '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=10.3.6.51)(PORT=1521) ))' \
             '(CONNECT_DATA=(service_name=analyse.gtbank.com)))'

conf = {
    "apikeys": {
        "gtapp01": {
            "app_key":"zXR2BFtRreCMX3XzLbJUVRQLz",
            "app_secret":"3nAN9aWljxxNP7xvZrnC4ci1wuynVTKVARvLec24LnbDNPMdDM",
            "oauth_token":"2342906806-rnVpZYSxnvedx7TdTOpcVzyer7J1tiUtescGnMF",
            "oauth_token_secret":"KBxmwFAhE5gACR8K4fvXW2MNQztBvIHgGClEiDEsarLFw"
        }
        ,
        "gtapp02" :{
            "app_key":"znUmqqDiyVDM1bJbz2hrYPmc0",
            "app_secret":"T2qj7XH7g2DRGreuhk43p71Ny35XmWevuCUHBC5DIxi7QRLy6a",
            "oauth_token":"2342906806-qOKx544CIfatYtV15Ij2b3z45PzLzOe1RTcSPbB",
            "oauth_token_secret":"axRVf4w6oGRll9a3oV6eMwxa9tJJDPwhJpYhMg9wQswFP"
        },
        "gtapp03" :{
            "app_key":"xGkrCs5P93gHzKGttks7tZlNS",
            "app_secret":"xKIZxcvUMcahot8aREJSSuQFcKwNInXUMcOOAwv4RpZeQEEqvH",
            "oauth_token":"	2342906806-rFclg4mcZX8rONaYdwCRcel6NwgX34jPpUNMvZk",
            "oauth_token_secret":"hJLrmSnLIziF60NdWN7TvQcIH5xMjT2wPJQzcc1UVF78G"
        },
        "gtapp04" :{
            "app_key":"P5nxHs5XXo9rWqQ72YRB31ZV1",
            "app_secret":"Bhbp6YgWvmBxqPSouCdC96BYLGzAe1yodbeLe2Uqr0Z1aB4QBC",
            "oauth_token":"	2342906806-GGdoJhVYUJMC51MPGhxyB782IpMzJfc3v1gYSPk",
            "oauth_token_secret":"0ILdXUN1EmkqwrJlltH6eurc4rL62UH9D7JqJTR0cAQFp"
        }
    },
    "handler": {
            "name": "FileHandler",
            "args": {"output_folder": OUT_FOLDER}
            },
    "redis_config": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None
    },
    "verbose": "True",
    "output": OUT_FOLDER,
    "archive_output": ARCHIVE_FOLDER,
    "check_proxies":False
}