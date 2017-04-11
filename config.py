from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

output_folder = "./data"

proxies  = 'tests/proxies.json'

conf = {
	"apikeys": {
		"i0mf0rmer01" :{
			"app_key":"zXR2BFtRreCMX3XzLbJUVRQLz",
			"app_secret":"3nAN9aWljxxNP7xvZrnC4ci1wuynVTKVARvLec24LnbDNPMdDM",
			"oauth_token":"2342906806-rnVpZYSxnvedx7TdTOpcVzyer7J1tiUtescGnMF",
			"oauth_token_secret":"KBxmwFAhE5gACR8K4fvXW2MNQztBvIHgGClEiDEsarLFw"
		}
		# ,
		# "i0mf0rmer02" :{
		# 	"app_key":"CONSUMER_KEY-2",
		# 	"app_secret":"CONSUMER_SECRET",
		# 	"oauth_token":"ACCESS_TOKEN",
		# 	"oauth_token_secret":"ACCESS_TOKEN_SECRET"
		# },
		# "i0mf0rmer03" :{
		# 	"app_key":"CONSUMER_KEY-3",
		# 	"app_secret":"CONSUMER_SECRET",
		# 	"oauth_token":"ACCESS_TOKEN",
		# 	"oauth_token_secret":"ACCESS_TOKEN_SECRET"
		# }
	}, 
	"handler": {
			"name": "FileHandler",
			"args": {"output_folder" : output_folder}
			},		
	"redis_config": {
		"host": "localhost",
		"port": 6379,
		"db": 0,
		"password": None
	},
	"verbose": "True",
	"output": output_folder,
	"archive_output":output_folder
}