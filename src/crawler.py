import couchdb
import sys
import atexit
import datetime
import pandas as pd
import yaml
from harvesters import StreamTweetHarvester, KeywordsHarvester
from preprocessors import Preprocessor
from database_saver import Database
import threading
import pika


def get_tracking_keywords(configs):
	df = pd.read_csv(configs['party_features'], encoding = "ISO-8859-1")
	keywords = configs['keywords']

	# Add party twitter page
	for text in df[df.twitter.notnull()].twitter.values:
		keywords.extend(['@' + x.strip() for x in text.split(',')])

	# Add party name
	for text in df[df.party_name.notnull()].party_name.values:
		keywords.extend([x.lower().strip() for x in text.split(',')])

	# Add party abbr name
	for text in df[df.abbr.notnull()].abbr.values:
		keywords.extend([x.lower().strip() for x in text.split(',')])

	# Add leader name
	for text in df[df.leader.notnull()].leader.values:
		keywords.extend([x.lower().strip() for x in text.split(',')])

	# Add leader twitter
	for value in df[df.leader_twitter.notnull()].leader_twitter.values:
		keywords.extend(['@' + x.strip() for x in value.split(',')])

	return keywords


def pre_check_files():
	try:
		with open("config.yaml", 'r') as ymlfile:
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
	harvester.start_harvesting()


def start_preprocessor(preprocessor):
	preprocessor.start_processing()


def start_database(database):
	database.start_saving()


def run_app(harvester_type, twitter_credential, boundary, keywords, database, configs):
	harvester = None
	preprocessor = Preprocessor(configs, boundary, keywords)
	if harvester_type == configs['APP_DATA']['harvester_type_1']:
		harvester = StreamTweetHarvester(twitter_credential, boundary, keywords, configs['QUEUE'])
	elif harvester_type == configs['APP_DATA']['harvester_type_2']:
		harvester = KeywordsHarvester(twitter_credential, boundary, keywords, configs['QUEUE'])
	else:
		harvester = StreamTweetHarvester(twitter_credential, boundary, keywords, configs['QUEUE'])
	print(datetime.datetime.now(), "tweeter user in use ", twitter_credential.id)

	harvester_thread = threading.Thread(target=start_harvester, args=(harvester,))
	processing_thread = threading.Thread(target=start_preprocessor, args=(preprocessor,))
	database_thread = threading.Thread(target=start_database, args=(database,))

	harvester_thread.start()
	processing_thread.start()
	database_thread.start()

	harvester_thread.join()


def exit_handler(database):
	print(datetime.datetime.now(), " : ", 'Application is ending!')
	database.unlock_twitter_account()


def main(argv):
	configs = pre_check_files()
	database = Database(configs)
	boundary = configs['APP_DATA']['boundary']
	keywords = get_tracking_keywords(configs['APP_DATA'])

	user = database.get_twitter_credential()
	atexit.register(exit_handler, database)
	try:
		harvester_type = 'api_streamline'
		if len(argv) > 1:
			harvester_type = argv[1]
		run_app(harvester_type, user, boundary, keywords, database, configs)
	except KeyboardInterrupt:
		exit_handler(database)
	finally:
		exit_handler(database)


if __name__ == "__main__":
	main(sys.argv)


