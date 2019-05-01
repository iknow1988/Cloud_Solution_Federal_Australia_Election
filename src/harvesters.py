from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import helper
import json
from shapely.geometry import shape, Point, Polygon


class StdOutListener(StreamListener):

	def __init__(self, boundary, boundary_polygon, tweet_db, users_db):
		self.BOUNDARY = boundary
		self.BOUNDARY_POLYGON = boundary_polygon
		self.tweet_db = tweet_db
		self.users_db = users_db

	def on_data(self, data):
		data = json.loads(data)
		if helper.tweet_in_australia_boundary(self.BOUNDARY, self.BOUNDARY_POLYGON, data["coordinates"],
											  data['geo'], data['place']):
			try:
				self.tweet_db[data['id_str']] = data
				user = data['user']['id_str']
				print(data['id_str'], " saved to tweeter database")
				if user not in self.users_db:
					self.users_db[user] = {'screen_name': data['user']['screen_name']}
					print("\tnew ", user, "added to user database")
			except:
				print(data['id_str'], " already exists")

		return True

	def on_error(self, status):
		print(status)


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

	def start_harvesting(self):
		l = StdOutListener(self.boundary, self.boundary_polygon, self.tweet_db, self.users_db)
		auth = OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)
		stream = Stream(auth, l)
		stream.filter(track=self.tags, locations=self.boundary, languages=["en"])


class TimeLineHarvester(Harvester):

	def __init__(self):
		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)
		self.api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]))

	def get_all_tweets(self,screen_name):
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
		count = 0

		for counter, tweet in enumerate(all_tweets):
			data = tweet._json
			if helper.tweet_in_australia(data["coordinates"], data['geo'], data['place']):
				try:
					self.tweet_db[data['id_str']] = data
					count = count + 1
				except:
					pass
			# print("Tweet in database")
			if count and counter % 100 == 0:
				print("Left to save to database: ", len(all_tweets) - counter)
		if count:
			print("Saved %s tweets to database" % count, "for user:", screen_name)

	def start_harvesting(self):
		rows = len(self.users_db)
		print(rows)
		for index, id in enumerate(self.users_db):
			doc = self.users_db[id]
			name = doc['screen_name']
			print(name)
			if 'processed' not in doc:
				self.get_all_tweets(name)
				doc['processed'] = 1
				try:
					self.users_db.save(doc)
					print("Updated %s database" % name)
				except:
					print("%s database update error" % name)
			else:
				print("User already processed")
			print("left:", rows - index)
