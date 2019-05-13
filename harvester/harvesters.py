from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import json
import datetime
import time
from http.client import IncompleteRead
from urllib3.exceptions import ProtocolError
import pika


class Harvester:

	def __init__(self, twitter_credential, boundary, tags, config):
		self.boundary = boundary
		self.access_token = twitter_credential['access_token']
		self.access_token_secret = twitter_credential['access_token_secret']
		self.consumer_key = twitter_credential['consumer_key']
		self.consumer_secret = twitter_credential['consumer_secret']
		self.tags = tags
		self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
		self.auth.set_access_token(self.access_token, self.access_token_secret)
		self.api = API(self.auth, wait_on_rate_limit=True, retry_count=3, retry_delay=5, retry_errors = set([401, 404, 500, 503]))
		credentials = pika.PlainCredentials(config['queue_user'], config['queue_password'])
		parameters = pika.ConnectionParameters(config['queue_server'], config['queue_port'], '/', credentials)
		connection = pika.BlockingConnection(parameters)
		self.channel = connection.channel()
		self.channel.queue_declare(queue=config['queue_preprocess'])

	def start_harvesting(self):
		pass

	def send_tweet_to_process(self, data):
		text = None
		if 'extended_tweet' in data and data['extended_tweet']:
			text = data['extended_tweet']['full_text']
		elif 'text' in data and data['text']:
			text = data['text']
		else:
			text = None
		if text:
			self.channel.basic_publish(exchange='', routing_key='preprocess', body=json.dumps(data))

	def send_tweets_to_process(self, all_tweets):
		for index, tweet in enumerate(all_tweets):
			data = tweet._json
			self.send_tweet_to_process(data)


class StdOutListener(StreamListener):

	def __init__(self, harvester):
		self.harvester = harvester

	def on_data(self, data):
		data = json.loads(data)
		self.harvester.send_tweet_to_process(data)
		return True

	def on_error(self, status):
		print(datetime.datetime.now(), " : " , status)


class StreamTweetHarvester(Harvester):

	def __init__(self, twitter_credential, boundary, tags, config):
		Harvester.__init__(self, twitter_credential, boundary, tags, config)

	def start_harvesting(self):
		stream = Stream(self.auth, StdOutListener(self))
		while True:
			try:
				stream.filter(track=self.tags)
			except IncompleteRead:
				stream.filter(track=self.tags)
				continue
			except (ProtocolError, AttributeError):
				continue
			except KeyboardInterrupt:
				stream.disconnect()
				break


class TimeLineHarvester(Harvester):

	def __init__(self, twitter_credential, boundary, tags, twitter_ids, config):
		Harvester.__init__(self, twitter_credential, boundary, tags, config)
		self.twitter_screen_names = twitter_ids

	def get_all_tweets(self, screen_name):
		all_tweets = []
		try:
			new_tweets = self.api.user_timeline(screen_name=screen_name, count=200)
			all_tweets.extend(new_tweets)
			oldest = all_tweets[-1].id - 1
		except:
			new_tweets = []
			pass
		while len(new_tweets) > 0:
			try:
				new_tweets = self.api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
			except:
				pass
			all_tweets.extend(new_tweets)
			oldest = all_tweets[-1].id - 1
		print(datetime.datetime.now(), " : ", "Downloaded tweets", len(new_tweets), " for user:", screen_name)
		self.send_tweets_to_process(all_tweets)
		time.sleep(5)

	def start_harvesting(self):
		rows = len(self.twitter_screen_names)
		for index, screen_name in enumerate(self.twitter_screen_names):
			print(datetime.datetime.now(), " : ", "Processing", " : ", screen_name)
			self.get_all_tweets(screen_name)
			print(datetime.datetime.now(), " : ", " Users left:", rows - index)


class KeywordsHarvester(Harvester):

	def __init__(self, twitter_credential, boundary, tags, config):
		Harvester.__init__(self, twitter_credential, boundary, tags, config)

	def get_all_tweets(self, search_query, max_id=None, since_id=None):
		tweet_count = 0
		tweets_per_query = 100
		max_tweets = 50000
		geo = "-31.53162668535551,135.53294849999997,2514.0km"
		while tweet_count < max_tweets:
			if not max_id:
				if not since_id:
					new_tweets = self.api.search(q=search_query, count=tweets_per_query, geocode = geo)
				else:
					new_tweets = self.api.search(q=search_query, count=tweets_per_query, since_id=since_id, geocode = geo)
			else:
				if not since_id:
					new_tweets = self.api.search(q=search_query, geocode = geo, count=tweets_per_query, max_id=str(max_id - 1))
				else:
					new_tweets = self.api.search(q=search_query, count=tweets_per_query, max_id=str(max_id - 1), since_id=since_id, geocode = geo)
			if not new_tweets:
				print(datetime.datetime.now(), " : ", "No new tweets to show")
				break
			print(datetime.datetime.now(), " : ", " downloaded ", len(new_tweets), " tweets", " and maxid", max_id)
			tweet_count += len(new_tweets)
			self.send_tweets_to_process(new_tweets)
			max_id = new_tweets[-1].id
			time.sleep(5)

	def start_harvesting(self):
		tags = self.tags
		n = 0
		keywords = list()
		index = 0
		for word in tags:
			words = word.split(' ')
			if len(words) > 2:
				keyword = word
				print(index, datetime.datetime.now(), " STARTED WITH: ", word)
				self.get_all_tweets(search_query = keyword, max_id= None)
				index = index + 1
			else:
				n = n + len(words)
				if n < 8:
					keywords.append(word)
				else:
					keyword = ' OR '.join(keywords)
					print(index, datetime.datetime.now(), " STARTED WITH: ", keywords)
					self.get_all_tweets(search_query = keyword, max_id= None)
					n = 0
					keywords = list()
					index = index + 1


