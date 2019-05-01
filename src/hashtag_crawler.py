from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
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

