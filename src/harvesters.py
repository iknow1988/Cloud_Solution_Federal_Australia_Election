from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import helper
import json
from shapely.geometry import shape, Point, Polygon
import datetime


class StdOutListener(StreamListener):

	def __init__(self, boundary, boundary_polygon, tweet_db, users_db):
		self.boundary = boundary
		self.boundary_polygon = boundary_polygon
		self.tweet_db = tweet_db
		self.users_db = users_db

	def on_data(self, data):
		data = json.loads(data)
		if helper.tweet_in_australia_boundary(self.boundary, self.boundary_polygon, data["coordinates"],
											  data['geo'], data['place']):
			try:
				self.tweet_db[data['id_str']] = data
				user = data['user']['id_str']
				print(datetime.datetime.now(), " : " ,data['id_str'], " saved to tweeter database")
				if user not in self.users_db:
					self.users_db[user] = {'screen_name': data['user']['screen_name']}
			except:
				print(datetime.datetime.now(), " : " , data['id_str'], " already exists")

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

	def start_harvesting(self):
		pass

	def save_tweets_to_db(self, all_tweets, user_id):
		count = 0
		for counter, tweet in enumerate(all_tweets):
			data = tweet._json
			if helper.tweet_in_australia(data["coordinates"], data['geo'], data['place']):
				try:
					self.tweet_db[data['id_str']] = data
					count = count + 1
				except:
					pass
		if count:
			print(datetime.datetime.now(), " : ", "Saved %s tweets to database" % count, "for user:", user_id)


class StreamTweetHarvester(Harvester):

	def __init__(self, user, boundary, tags, tweet_db, users_db):
		Harvester.__init__(self, user, boundary, tags, tweet_db, users_db)

	def start_harvesting(self):
		l = StdOutListener(self.boundary, self.boundary_polygon, self.tweet_db, self.users_db)
		stream = Stream(self.auth, l)
		if self.tags and self.boundary:
			stream.filter(track=self.tags, locations=self.boundary)
		elif self.tags:
			stream.filter(track=self.tags)
		else:
			stream.filter(locations=self.boundary)


class TimeLineHarvester(Harvester):

	def __init__(self, user, user_id, screen_name, boundary, boundary_polygon, tweet_db, users_db):
		Harvester.__init__(self, user, boundary, boundary_polygon, tweet_db, users_db)
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
