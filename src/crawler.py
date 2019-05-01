import couchdb
import json
import sys
from hashtag_crawler import Harvester

COUCH_SERVER = couchdb.Server("http://admin:group2@115.146.84.108:9584/")
credential_db = COUCH_SERVER['tweeter_credentials']
TAGS = ['auspol', 'auspol2019', 'ausvotes2019', 'ausvotes19',
			 'bill shorten', 'happyclappersloganbogan', 'labor', 'dutton',
			 'lnpcorruption', 'ausvote2019', 'scott morrison', 'scott morrison church', 'thedrum']

try:
	tweet_db = COUCH_SERVER.create('election_geo_twitter')
except:
	tweet_db = COUCH_SERVER['election_geo_twitter']
users_db = COUCH_SERVER['users_twitter']


def app(user, boundary):
	boundary = [int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])]
	harvester = Harvester(user, boundary, TAGS, tweet_db, users_db)
	harvester.start_harvesting()


def main(argv):
	user = None
	xmin = int(argv[1])
	xmax = int(argv[3])
	ymin = int(argv[2])
	ymax = int(argv[4])
	boundary = [xmin, ymin, xmax, ymax]
	for index, id in enumerate(credential_db):
		doc = credential_db[id]
		if doc['in_use'] == 0:
			user = doc
			doc['in_use'] = 1
			try:
				credential_db.save(doc)
			except:
				print("Couldn't lock user")
				exit(0)
			break
	if user:
		try:
			print(user.id," is in use")
			app(user, boundary)
		finally:
			doc = credential_db[user['_id']]
			doc['in_use'] = 0
			credential_db.save(doc)
			print(user['_id'], " is unlocked")
	else:
		print("No user available")
	return 0


if __name__ == "__main__":
	argv = sys.argv
	main(argv)

