from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import couchdb
import json
import datetime

# Couchdb configure
couch = couchdb.Server('http://admin:group2@115.146.84.108:9584/')

try:
	db = couch.create('raw_twitter')
except:
	db = couch['raw_twitter']
users_db = couch['users_twitter']


# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

	def on_data(self, data):
		try:
			data = json.loads(data)
			data['processed'] = 1
			db[data['id_str']] = data
			user = data['user']['id_str']
			print(data['id_str'], " saved to tweeter database")
			if user not in users_db:
				users_db[user] = {'count': 1, 'tweets': [data['id_str']], 'screen_name': data['user']['screen_name']}
				print("\tnew ",user, "added to user database")
			else:
				data_user = users_db[user]
				data_user['tweets'].append(data['id_str'])
				data_user['count'] = data_user['count'] + 1
				data_user['screen_name'] = data['user']['screen_name']
				users_db[user] = data_user
				print("\t", user, " updated user database")
		except:
			print(data['id_str'], " Can not save to database")

		return True

	def on_error(self, status):
		print(status)


def main():
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)
	stream.filter(locations=[111, -44, 157, -10],languages= ["en"])
	stream.sample()
	return 0

if __name__ == "__main__":
	print(datetime.datetime.now())
	# main()