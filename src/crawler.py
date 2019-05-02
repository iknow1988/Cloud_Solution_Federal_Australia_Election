import couchdb
import json
import sys
import atexit
from harvesters import StreamTweetHarvester, TimeLineHarvester
import datetime
import pandas as pd
from nltk.tokenize import word_tokenize

COUCH_SERVER = couchdb.Server("http://admin:group2@115.146.84.108:9584/")
credential_db = COUCH_SERVER['tweeter_credentials']
TAGS = ['auspol', 'auspol2019', 'ausvotes2019', 'ausvotes19',
		'bill shorten', 'happyclappersloganbogan', 'labor', 'dutton',
		'lnpcorruption', 'ausvote2019', 'scott morrison', 'scott morrison church', 'thedrum',
		'BillShorten']

try:
	tweet_db = COUCH_SERVER.create('election_geo_twitter')
except:
	tweet_db = COUCH_SERVER['election_geo_twitter']
users_db = COUCH_SERVER['users_twitter']
followers_db = COUCH_SERVER['followers']

def app(user, boundary):
	harvester = StreamTweetHarvester(user, boundary, get_tags(), tweet_db, users_db)
	harvester.start_harvesting()


def app_timeline(user, boundary):
	harvester = TimeLineHarvester(user, None, None, boundary, get_tags(), tweet_db, followers_db)
	harvester.start_harvesting()


def prepare_harvester_parameters(option):
	parameters={
		'kazi': [141,-35,159,-8],
		'nafis': [129,-41,141,-9],
		'unknown1': [141,-44,154,-35],
		'unknown2': [110,-37,129,-10],
		'daniel':[110,-44,159,-8]
	}
	return parameters[option]


def get_tags():
	df = pd.read_csv('australia.csv', encoding = "ISO-8859-1")
	temp = TAGS
	temp.extend([x.lower() for x in df.party_name.values])
	temp.extend([x.lower() for x in df[df.abbr.notnull()].abbr.values])
	temp.extend([x.lower() for x in df[df.leader.notnull()].leader.values])
	for text in df[df.ideology.notnull()].ideology.values:
		tokenized = [x.lower().strip() for x in text.split(',')]
		temp.extend(tokenized)

	return temp

def streamline(argv):
	try:
		for index, id in enumerate(credential_db):
			doc = credential_db[id]
			if argv[1] == id:
				if doc['in_use'] == 0:
					user = doc
					doc['in_use'] = 1
					try:
						credential_db.save(doc)
						atexit.register(exit_handler, user)
						break
					except:
						print("Couldn't lock user")
						exit(0)
				else:
					print(id, " is locked")
		if user:
			print(datetime.datetime.now(), " : ", user.id, " is in use for", prepare_harvester_parameters(id))
			app(user, prepare_harvester_parameters(id))
		else:
			print(datetime.datetime.now(), " Error ")
	finally:
		exit_handler(user)

	return 0


def timeline():
	user = None
	doc = credential_db['daniel']
	if doc['in_use'] == 0:
		user = doc
		doc['in_use'] = 1
		try:
			credential_db.save(doc)
			atexit.register(exit_handler, user)
		except:
			print("Couldn't lock user")
			exit(0)
	else:
		print(id, " is locked")

	if user:
		print(datetime.datetime.now(), " : ", user.id, " is in use for", prepare_harvester_parameters(user.id))
		app_timeline(user, prepare_harvester_parameters(user.id))
	else:
		print(datetime.datetime.now(), " Error ")

def main(argv):
	if len(argv) > 1:
		streamline(argv)
	else:
		timeline()



def exit_handler(user):
	print('My application is ending!')
	if user:
		for index, id in enumerate(credential_db):
			doc = credential_db[id]
			if user.id == id:
				if doc['in_use'] == 1:
					user = doc
					doc['in_use'] = 0
					credential_db.save(doc)
					print(user['_id'], " is unlocked")


if __name__ == "__main__":
	# print(len(list(set(get_tags()))))
	main(sys.argv)

