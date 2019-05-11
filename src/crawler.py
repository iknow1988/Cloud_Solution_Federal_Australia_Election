import couchdb
import sys
import atexit
from harvesters import StreamTweetHarvester, KeywordsHarvester
from helper import Preprocessor
import datetime
import pandas as pd
import yaml


def get_databases(configs):
	tweet_db = None
	users_db = None
	credential_db = None
	try:
		connection_param = "http://%s:%s@%s:%s/" % (configs['user'], configs['password'],
													configs['ip'], configs['port'])
		couch_server = couchdb.Server(connection_param)
	except Exception as e:
		print(datetime.datetime.now(), " : ", e[1])
		exit()

	try:
		tweet_db = couch_server.create(configs['tweet_db'])
	except Exception as e:
		if type(e).__name__ == 'PreconditionFailed':
			tweet_db = couch_server[configs['tweet_db']]
		else:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

	try:
		users_db = couch_server.create(configs['users_db'])
	except Exception as e:
		if type(e).__name__ == 'PreconditionFailed':
			users_db = couch_server[configs['users_db']]
		else:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

	try:
		credential_db = couch_server[configs['credential_db']]
	except Exception as e:
		template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

	if tweet_db and users_db and credential_db:
		databases = [tweet_db, users_db, credential_db]
		return databases
	else:
		print(datetime.datetime.now(), " : ", "Database configuration error")
		exit(0)


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


def get_twitter_credentials(credential_db):
	user = None
	for index, id in enumerate(credential_db):
		doc = credential_db[id]
		if doc['in_use'] == "0":
			user = doc
			doc['in_use'] = "1"
			try:
				credential_db.save(doc)
				break
			except:
				print(datetime.datetime.now(), "Couldn't lock user")
				exit(0)
	if not user:
		print(datetime.datetime.now(), " Couldn't lock any user ")
		exit(0)

	return user


def run_app(harvester_type, twitter_credential, boundary, keywords ,databases, configs):
	harvester = None
	preprocessor = Preprocessor(configs, boundary, keywords, databases)
	if harvester_type == configs['harvester_type_1']:
		harvester = StreamTweetHarvester(twitter_credential, boundary, keywords, preprocessor)
	elif harvester_type == configs['harvester_type_2']:
		harvester = KeywordsHarvester(twitter_credential, boundary, keywords, preprocessor)
	else:
		harvester = StreamTweetHarvester(twitter_credential, boundary, keywords, preprocessor)
	print(datetime.datetime.now(), "tweeter user in use ", twitter_credential.id)

	harvester.start_harvesting()


def exit_handler(user, credential_db):
	print(datetime.datetime.now(), " : ", 'Application is ending!')
	if user:
		doc = credential_db[user['_id']]
		if doc['in_use'] == "1":
			user = doc
			doc['in_use'] = "0"
			credential_db.save(doc)
			print(datetime.datetime.now(), " : ", user['_id'], " is unlocked")


def main(argv):
	with open("config.yaml", 'r') as ymlfile:
		configs = yaml.load(ymlfile, Loader=yaml.FullLoader)
		ymlfile.close()
	databases = get_databases(configs['COUCHDB'])
	boundary = configs['APP_DATA']['boundary']
	keywords = get_tracking_keywords(configs['APP_DATA'])

	credential_db = databases[2]
	user = get_twitter_credentials(credential_db)
	atexit.register(exit_handler, user, credential_db)
	try:
		harvester_type = 'api_streamline'
		if len(argv) > 1:
			harvester_type = argv[1]
		run_app(harvester_type, user, boundary, keywords, databases, configs['APP_DATA'])
	except KeyboardInterrupt:
		exit_handler(user, credential_db)
	finally:
		exit_handler(user, credential_db)


if __name__ == "__main__":
	main(sys.argv)


