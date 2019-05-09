from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import helper
import json
from shapely.geometry import shape, Point, Polygon
import datetime
import time
from http.client import IncompleteRead
from urllib3.exceptions import ProtocolError
import re


class StdOutListener(StreamListener):

	def __init__(self, harvester):
		self.harvester = harvester

	def on_data(self, data):
		data = json.loads(data)
		self.harvester.save_tweet_to_db(data)
		return True

	def on_error(self, status):
		print(datetime.datetime.now(), " : " , status)


class Harvester:

	def __init__(self, twitter_credential, boundary, tags, databases):
		self.boundary = boundary
		x_min = float(boundary[0])
		x_max = float(boundary[2])
		y_min = float(boundary[1])
		y_max = float(boundary[3])
		self.boundary_polygon = Polygon([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]])
		self.access_token = twitter_credential['access_token']
		self.access_token_secret = twitter_credential['access_token_secret']
		self.consumer_key = twitter_credential['consumer_key']
		self.consumer_secret = twitter_credential['consumer_secret']
		self.tags = tags
		self.tweet_db = databases[0]
		self.users_db = databases[1]
		self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
		self.auth.set_access_token(self.access_token, self.access_token_secret)
		self.election_seat_polygons = helper.initialize_election_map()
		self.gcc_polygons = helper.initialize_gcc_map()
		self.party_features = helper.get_party_features()
		self.regex = re.compile('[^a-zA-Z0-9_ ]')
		self.locations = helper.initialize_location_dictionaries()
		self.api = API(self.auth, wait_on_rate_limit=True, retry_count=3, retry_delay=5, retry_errors = set([401, 404, 500, 503]))

	def start_harvesting(self):
		pass

	def get_party(self, doc):
		parties = []
		doc_processed = self.regex.sub('', doc).strip().lower()
		for party, party_features in self.party_features.items():
			features = ["\\b(" + x + ")\\b" for x in party_features]
			keywords = "|".join(features)
			regex2 = re.compile(keywords)
			found = regex2.findall(doc_processed)
			if found:
				parties.append(party)

		if len(parties)>0:
			return parties
		else:
			return None

	def save_tweet_to_db(self, data, print_status = True):
		result = False
		text = None
		if 'extended_tweet' in data and data['extended_tweet']:
			text = data['extended_tweet']['full_text']
			party = self.get_party(text)
		elif 'text' in data and data['text']:
			text = data['text']
			party = self.get_party(text)
		else:
			party = None
		geo_data = self.get_geo_location(data)
		if geo_data and text and party:
			try:
				user = data['user']['id_str']
				data['city'] = geo_data [0]
				data['state'] = geo_data[1]
				data['country'] = geo_data[2]
				data['party'] = party
				data['processed_text'] = helper.get_processed_tweet(text)
				sentiment_scores = helper.get_polarity_score(text)
				data['tweet_intensity'] = sentiment_scores['intensity']
				data['tweet_sentiment'] = sentiment_scores['sentiment']
				self.tweet_db[data['id_str']] = data
				if print_status:
					print(datetime.datetime.now(), " : ", data['id_str'], " saved to tweeter database")
				result = True
				if user not in self.users_db:
					self.users_db[user] = {'screen_name': data['user']['screen_name']}
			except:
				if print_status:
					print(datetime.datetime.now(), " : " , data['id_str'], " already exists")
		return result

	def save_tweets_to_db(self, all_tweets):
		count = 0
		for index, tweet in enumerate(all_tweets):
			data = tweet._json
			if self.save_tweet_to_db(data, False):
				count = count + 1
		if count:
			print(datetime.datetime.now(), " : ", "Saved %s tweets to database" % count)

	def get_geo_location(self, data):
		loc = helper.tweet_in_australia_boundary(data, self)
		return loc


class StreamTweetHarvester(Harvester):

	def __init__(self, twitter_credential, boundary, tags, databases):
		Harvester.__init__(self, twitter_credential, boundary, tags, databases)

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

	def __init__(self, twitter_credential, boundary, tags, databases, twitter_ids):
		Harvester.__init__(self, twitter_credential, boundary, tags, databases)
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
		self.save_tweets_to_db(all_tweets)
		time.sleep(5)

	def start_harvesting(self):
		rows = len(self.twitter_screen_names)
		for index, screen_name in enumerate(self.twitter_screen_names):
			print(datetime.datetime.now(), " : ", "Processing", " : ", screen_name)
			self.get_all_tweets(screen_name)
			print(datetime.datetime.now(), " : ", " Users left:", rows - index)


class KeywordsHarvester(Harvester):

	def __init__(self, twitter_credential, boundary, tags, databases):
		Harvester.__init__(self, twitter_credential, boundary, tags, databases)

	def get_all_tweets(self, search_query, max_id=None, since_id=None):
		tweet_count = 0
		tweets_per_query = 100
		max_tweets = 40000
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
			self.save_tweets_to_db(new_tweets)
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


