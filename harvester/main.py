#####################################
# COMP 90024
# GROUP NUMBER : 2
# CITY         : Melbourne
# GROUP MEMBERS:
#  - Kazi Abir Adnan - 940406>
#  - Ahmed Fahmin - 926184
#  - Mohammad Nafis Ul Islam - 926190
#  - Daniel Gil - 905923
#  - Kun Chen - 965513
####################################

import atexit
import datetime
import pandas as pd
import yaml
from harvesters import StreamTweetHarvester, KeywordsHarvester
from preprocessors import Preprocessor
from database_saver import Database
import threading
import sys
import time


def get_tracking_keywords(configs):
	'''Returns tracking keywords to for tweet collections'''

	df = pd.read_csv(configs['party_features'], encoding = "ISO-8859-1")
	keywords = configs['keywords']

	# Add party twitter page
	for text in df[df.twitter.notnull()].twitter.values:
		keywords.extend(['@' + x.strip() for x in text.split(',')])

	# Add party name
	for text in df[df.party_name.notnull()].party_name.values:
		keywords.extend([x.lower().strip() for x in text.split(',')])

	# Add leader name
	for text in df[df.leader.notnull()].leader.values:
		keywords.extend([x.lower().strip() for x in text.split(',')])

	# Add leader twitter
	for value in df[df.leader_twitter.notnull()].leader_twitter.values:
		keywords.extend(['@' + x.strip() for x in value.split(',')])

	return keywords


def pre_check_files(argv):
	'''Check whether required files are present to run'''

	if len(argv)>1:
		file_name = 'logs/log_'+argv[1]+'.txt'
	else:
		file_name = 'logs/log_api_streamline.txt'

	sys.stdout = open(file_name, 'a+')

	try:
		with open("../config.yaml", 'r') as ymlfile:
			configs = yaml.load(ymlfile)
			# configs = yaml.load(ymlfile, Loader=yaml.FullLoader)
			ymlfile.close()
	except Exception as e:
		template = "An exception of type {0} occurred due to config file not found. Arguments:\n{1!r}"
		print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))
		exit(0)
	try:
		exists = open(configs['APP_DATA']['party_features'], 'r')
		exists = open(configs['APP_DATA']['election_map_shape_file'], 'r')
		exists = open(configs['APP_DATA']['gcc_map_shape_file'], 'r')
		exists = open(configs['APP_DATA']['australia_city_names'], 'r')
		exists = open(configs['APP_DATA']['aurin_data_locations'], 'r')
	except FileNotFoundError:
		print(datetime.datetime.now(), " : One of the Data files in configuration not found")
		exit(0)

	return configs


def start_harvester(harvester):
	'''Thread function to start the harvester'''

	harvester.start_harvesting()


def start_preprocessor(preprocessor):
	'''Thread function to start the preprocessor'''

	preprocessor.start_processing()


def start_database(database):
	'''Thread function to start the database'''
	database.start_saving()


def run_app(harvester_type, twitter_credential, boundary, keywords, database, configs):
	'''Function to launch the application of harvester'''

	preprocessor = Preprocessor(configs, boundary, keywords)
	if harvester_type == configs['APP_DATA']['harvester_type_1']:
		harvester = StreamTweetHarvester(twitter_credential, boundary, keywords, configs)
	elif harvester_type == configs['APP_DATA']['harvester_type_2']:
		harvester = KeywordsHarvester(twitter_credential, boundary, keywords, configs)
	else:
		harvester = StreamTweetHarvester(twitter_credential, boundary, keywords, configs)
	print(datetime.datetime.now(), "tweeter user in use ", twitter_credential.id)

	harvester_thread = threading.Thread(target=start_harvester, args=(harvester,))
	processing_thread = threading.Thread(target=start_preprocessor, args=(preprocessor,))
	database_thread = threading.Thread(target=start_database, args=(database,))

	harvester_thread.start()
	processing_thread.start()
	database_thread.start()

	harvester_thread.join()


def exit_handler(database):
	'''Exit function to stop the harvester'''

	print(datetime.datetime.now(), " : ", 'Application is ending!')
	database.unlock_twitter_account()
	sys.stdout.flush()
	exit(0)


def main(argv):
	while True:

		# precheck files
		configs = pre_check_files(argv)

		# launch database
		database = Database(configs)

		# set variables
		boundary = configs['APP_DATA']['boundary']
		keywords = get_tracking_keywords(configs['APP_DATA'])
		user = database.get_twitter_credential()
		atexit.register(exit_handler, database)

		# Run the application
		try:
			harvester_type = 'api_streamline'
			if len(argv) > 1:
				harvester_type = argv[1]
			run_app(harvester_type, user, boundary, keywords, database, configs)
		except KeyboardInterrupt:
			print(datetime.datetime.now(), " : ", "INTERRUPTED!")
			exit_handler(database)
		except Exception as generic:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			print(datetime.datetime.now(), " : ", template.format(type(generic).__name__, generic.args))
			database.unlock_twitter_account()
			time.sleep(120)
			continue
		else:
			database.unlock_twitter_account()
			continue


if __name__ == "__main__":
	main(sys.argv)


