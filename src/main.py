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

# Couchdb configure
couch = couchdb.Server('https://admin:group2@115.146.84.108:9584/')

try:
	db = couch.create('raw_twitter')
except:
	db = couch['raw_twitter']

# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

	def on_data(self, data):
		try:
			data = json.loads(data)
			db[data['id']] = data
		except:
			print("Can not save to database")

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