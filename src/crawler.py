import couchdb
import sys
import atexit
from harvesters import StreamTweetHarvester, KeywordsHarvester
import datetime
import pandas as pd

COUCH_SERVER = couchdb.Server("http://admin:password@103.6.254.59:9584/")
credential_db = COUCH_SERVER['tweeter_credentials']

TAGS = ['auspol','ausvotes','AusVotes19','ausvote2019' ,'auspol2019', 'ausvotes2019', 'ausvotes19',
		'bill shorten', 'dutton',
		'lnpcorruption','BillShorten','ScottMorrison', 'BuildingOurEconomy',
		'LeadersDebate2','LeadersDebate1','LeadersDebate']

try:
	tweet_db = COUCH_SERVER.create('tweeter_test')
except:
	tweet_db = COUCH_SERVER['tweeter_test']
users_db = COUCH_SERVER['users_twitter']


def app(user, boundary):
	harvester = StreamTweetHarvester(user, boundary, get_tags(), tweet_db, users_db)
	harvester.start_harvesting()


def app_keywords(user, boundary):
	harvester = KeywordsHarvester(user, boundary, get_tags(), tweet_db, users_db)
	harvester.start_harvesting()


def prepare_harvester_parameters(option):
	parameters={
		# 'kazi': [141,-35,159,-8],
		'kazi': [110,-44,159,-8],
		'nafis': [129,-41,141,-8],
		'unknown1': [141,-44,154,-35],
		'unknown2': [110,-37,129,-10],
		'daniel':[110,-44,159,-8],
		'kun':[110,-44,159,-8]
	}
	return parameters[option]


def get_tags():
	df = pd.read_csv('csv_files/political_party_attributes.csv', encoding = "ISO-8859-1")
	temp = TAGS
	temp.extend([x.lower() for x in df.party_name.values])

	for text in df[df.twitter.notnull()].twitter.values:
		tokenized = ['@' + x.strip() for x in text.split(',')]
		temp.extend(tokenized)

	for text in df[df.party_name.notnull()].party_name.values:
		tokenized = [x.lower().strip() for x in text.split(',')]
		temp.extend(tokenized)

	for text in df[df.abbr.notnull()].abbr.values:
		tokenized = [x.lower().strip() for x in text.split(',')]
		temp.extend(tokenized)

	for text in df[df.leader.notnull()].leader.values:
		tokenized = [x.lower().strip() for x in text.split(',')]
		temp.extend(tokenized)

	# for text in df[df.ideology.notnull()].ideology.values:
	# 	tokenized = [x.lower().strip() for x in text.split(',')]
	# 	temp.extend(tokenized)

	for value in df[df.leader_twitter.notnull()].leader_twitter.values:
		temp.extend(['@' + x.strip() for x in value.split(',')])

	print(len(temp))

	return temp

def streamline(argv):
	try:
		user = None
		for index, id in enumerate(credential_db):
			doc = credential_db[id]
			if argv[1] == id:
				if doc['in_use'] == "0":
					user = doc
					doc['in_use'] = "1"
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
	doc = credential_db['kun']
	if doc['in_use'] == "0":
		user = doc
		doc['in_use'] = "1"
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
		app_keywords(user, prepare_harvester_parameters(user.id))
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
				if doc['in_use'] == "1":
					user = doc
					doc['in_use'] = "0"
					credential_db.save(doc)
					print(user['_id'], " is unlocked")

def temp():
	df = pd.read_csv('australia.csv', encoding="ISO-8859-1")
	# temp = TAGS
	# temp.extend([x.lower() for x in df.party_name.values])
	party_mention = []
	abbr = []
	leader_name = []
	ideology = []
	leader_twitter_mentions = []
	party_name = []
	for text in df[df.twitter.notnull()].twitter.values:
		tokenized = [x.strip() for x in text.split(',')]
		party_mention.extend(tokenized)

	for text in df[df.abbr.notnull()].abbr.values:
		tokenized = [x.lower().strip() for x in text.split(',')]
		abbr.extend(tokenized)

	for text in df[df.leader.notnull()].leader.values:
		tokenized = [x.lower().strip() for x in text.split(',')]
		leader_name.extend(tokenized)

	for text in df[df.ideology.notnull()].ideology.values:
		tokenized = [x.lower().strip() for x in text.split(',')]
		ideology.extend(tokenized)

	for value in df[df.leader_twitter.notnull()].leader_twitter.values:
		leader_twitter_mentions.extend([x.strip() for x in value.split(',')])


	for value in df[df.party_name.notnull()].party_name.values:
		party_name.extend([x.lower().strip() for x in value.split(',')])

	print(party_name)
	print(abbr)
	print(party_mention)
	print(leader_name)
	print(leader_twitter_mentions)
	print(ideology)


if __name__ == "__main__":
	# print(len(list(set(get_tags()))))
	main(sys.argv)
	# temp()


