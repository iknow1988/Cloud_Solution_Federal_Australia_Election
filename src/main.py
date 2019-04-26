from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import couchdb
import json

#Variables that contains the user credentials to access Twitter API
# (This are all Kazi's credential)
access_token = "126540213-AEMmwT6f9qADYoZMYVgoWuneugkmSTNgRijcS8hT"
access_token_secret = "BfpYotAPGPA23B9dIcCicHR9r6YzwWFyhQx54SbVyXT6d"
consumer_key = "FjDcSP67VEq6N0XxIsQpr9BRR"
consumer_secret = "4qHx0cJvEwXD8u4yxKANVQP1mJ6oFNqHbEpELuo9l3SsSDKl1c"

# (This are all Daniel's credential)
# access_token = "16618497-snNvcNNuQjYhRCztSQ06dD6jT1lssjz7yLCaUHdiQ"
# access_token_secret = "vOXVTbz24FwSjUF2fQHDEdnZpER7HYHi3tgJRdO5COn82"
# consumer_key = "pULdzWMef98hVRYmyyuQXbD05"
# consumer_secret = "HaCFycsgw4uv010eV8e40nneTQbjAwFN7acIZoEkCU4Chhn0ur"

# Nafis
# access_token = "2680166335-Qz7Amfi0bc3gYaqnFxHmmH8BJVc10vN9mAOFuLB"
# access_token_secret = "DwgayvsCmqLaEkugcsssYjf8Zqw12tfgWldq6B2FS7DkV"
# consumer_key = "DzCD85X4wVcyL6AwPtFRwDxSZ"
# consumer_secret = "R8oyIchRZ3Y6wpEHQRTAZ14oV3AEZIRa8eLFnMaVo543QXsFkP"

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
	# This handles Twitter authetification and the connection to Twitter Streaming API
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)
	# This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
	#stream.filter(track=['python', 'javascript', 'ruby'])
	#locations= [140.3482679711,-39.7125077525,149.6598486874,-32.0871185235]
	stream.filter(locations=[111, -44, 157, -10],languages= ["en"])
	stream.sample()
	return 0

if __name__ == "__main__":
	main()