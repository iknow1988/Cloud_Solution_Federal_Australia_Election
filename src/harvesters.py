from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import helper
import json
from shapely.geometry import shape, Point, Polygon
import datetime
import pandas as pd
import time
from http.client import IncompleteRead


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

	def __init__(self, user, boundary, tags, tweet_db, users_db):
		self.boundary = boundary
		xmin = int(boundary[0])
		xmax = int(boundary[2])
		ymin = int(boundary[1])
		ymax = int(boundary[3])
		self.boundary_polygon = Polygon([[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]])
		self.access_token = user['access_token']
		self.access_token_secret = user['access_token_secret']
		self.consumer_key = user['consumer_key']
		self.consumer_secret = user['consumer_secret']
		self.tags = tags
		self.tweet_db = tweet_db
		self.users_db = users_db
		self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
		self.auth.set_access_token(self.access_token, self.access_token_secret)
		self.seat_polygons = helper.initialize_geo_map()
		self.sa4_polygons = helper.initialize_sa_4_map()

	def start_harvesting(self):
		pass

	def save_tweet_to_db(self, data, print_status = True):
		result = False
		if self.check_geo(data):
			try:
				seat, sa4 = self.get_seat_sa4(data)
				user = data['user']['id_str']
				if seat:
					data['seat'] = seat
				if sa4:
					data['sa4'] = sa4

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
		for counter, tweet in enumerate(all_tweets):
			data = tweet._json
			if self.save_tweet_to_db(data, False):
				count = count + 1
		if count:
			print(datetime.datetime.now(), " : ", "Saved %s tweets to database" % count)

	def check_geo(self, data):
		coordinates = None
		geo = None
		place = None
		location = None
		if "coordinates" in data:
			coordinates = data["coordinates"]
		if "geo" in data:
			geo = data['geo']
		if 'place' in data:
			place = data['place']
		if 'user' in data and 'location' in data['user']:
			location = data['user']['location']
		if helper.tweet_in_australia_boundary(self.boundary, self.boundary_polygon, coordinates, geo, place, location):
			return True
		else:
			return False

	def get_seat_sa4(self, data):
		locations = []
		big_locations = []
		if ('coordinates' in data and data['coordinates']) or ('geo' in data and data['geo']):
			for seat in self.seat_polygons:
				location = seat.give_location(data)
				if location:
					locations.append(location)
			for big in self.sa4_polygons:
				big_loc = big.give_location(data)
				if big_loc:
					big_locations.append(big_loc)
		if len(locations) == 1 :
			locations = locations [0]
		if len(big_locations) == 1:
			big_locations = big_locations[0]
		if locations or big_locations:
			print(locations, big_locations)
		return locations, big_locations


class StreamTweetHarvester(Harvester):

	def __init__(self, user, boundary, tags, tweet_db, users_db):
		Harvester.__init__(self, user, boundary, tags, tweet_db, users_db)

	def start_harvesting(self):
		l = StdOutListener(self)
		# l = StdOutListener(self.boundary, self.boundary_polygon, self.tweet_db, self.users_db)
		stream = Stream(self.auth, l)
		while True:
			try:
				stream.filter(track=self.tags)
			except IncompleteRead:
				continue
			except KeyboardInterrupt:
				stream.disconnect()
				break


class TimeLineHarvester(Harvester):

	def __init__(self, user, user_id, screen_name, boundary, tags, tweet_db, users_db):
		Harvester.__init__(self, user, boundary, tags, tweet_db, users_db)
		self.api = API(self.auth, wait_on_rate_limit=True, retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]))
		self.screen_name = screen_name
		self.user_id = user_id

	def get_all_tweets(self, user_id):
		all_tweets = []
		try:
			new_tweets = self.api.user_timeline(user_id=user_id, count=200)
			all_tweets.extend(new_tweets)
			oldest = all_tweets[-1].id - 1
		except:
			new_tweets = []
			pass
		while len(new_tweets) > 0:
			try:
				new_tweets = self.api.user_timeline(user_id=user_id, count=200, max_id=oldest)
			except:
				pass
			all_tweets.extend(new_tweets)
			oldest = all_tweets[-1].id - 1
		print(datetime.datetime.now(), " : ", "Downloaded tweets", len(new_tweets), " for user:", user_id)
		self.save_tweets_to_db(all_tweets, user_id)
		time.sleep(10)

	def start_harvesting(self):
		rows = len(self.users_db)
		for index, user_id in enumerate(self.users_db):
			doc = self.users_db[user_id]
			# name = doc['screen_name']
			print(datetime.datetime.now(), " : ", "Processing", " : ", user_id)
			if doc['processed'] == 0:
				self.get_all_tweets(user_id)
				doc['processed'] = 1
				try:
					self.users_db.save(doc)
				except:
					pass
			print(datetime.datetime.now(), " : ", " Users left:", rows - index)


class KeywordsHarvester(Harvester):

	def __init__(self, user, boundary, tags, tweet_db, users_db):
		Harvester.__init__(self, user, boundary, tags, tweet_db, users_db)
		self.api = API(self.auth, wait_on_rate_limit=True, retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]))

	def search_keyword(self, search_query, max_id=None, since_id=None):
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
					new_tweets = self.api.search(q=search_query, geocode = geo, count=tweets_per_query, max_id=str(max_id - 1), )
				else:
					new_tweets = self.api.search(q=search_query, count=tweets_per_query, max_id=str(max_id - 1),
											since_id=since_id, geocode = geo)
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
		exclude = list()
		for word in tags:
			words = word.split(' ')
			n = n + len(words)
			if len(words) > 2:
				print(datetime.datetime.now(), " STARTED WITH: ", word)
				keyword = word
				self.search_keyword(search_query = keyword, max_id= None)
				# n = 0
				# keywords = list()
			elif n < 10:
				keywords.append(word)
			else:
				print(datetime.datetime.now(), " STARTED WITH: ",keywords)
				keyword = ' OR '.join(keywords)
				self.search_keyword(search_query = keyword, max_id= None)
				n = 0
				keywords = list()


