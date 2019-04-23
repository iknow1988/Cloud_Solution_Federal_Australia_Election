from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API
access_token = "126540213-AEMmwT6f9qADYoZMYVgoWuneugkmSTNgRijcS8hT"
access_token_secret = "BfpYotAPGPA23B9dIcCicHR9r6YzwWFyhQx54SbVyXT6d"
consumer_key = "FjDcSP67VEq6N0XxIsQpr9BRR"
consumer_secret = "4qHx0cJvEwXD8u4yxKANVQP1mJ6oFNqHbEpELuo9l3SsSDKl1c"

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        print(data)
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
	stream.filter(track=['python', 'javascript', 'ruby'])
	return 0

if __name__ == "__main__":
	main()