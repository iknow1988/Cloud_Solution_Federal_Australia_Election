import re
import datetime
import helper
from shapely.geometry import shape, Point, Polygon
from mpi4py import MPI


class Saving_Layer:

	def __init__(self, boundary, databases, comm):
		self.boundary = boundary
		x_min = float(boundary[0])
		x_max = float(boundary[2])
		y_min = float(boundary[1])
		y_max = float(boundary[3])
		self.tweet_db = databases[0]
		self.users_db = databases[1]
		self.boundary_polygon = Polygon([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]])
		self.election_seat_polygons = helper.initialize_election_map()
		self.gcc_polygons = helper.initialize_gcc_map()
		self.party_features = helper.get_party_features()
		self.election_seat_polygons = helper.initialize_election_map()
		self.gcc_polygons = helper.initialize_gcc_map()
		self.party_features = helper.get_party_features()
		self.regex = re.compile('[^a-zA-Z0-9_ ]')
		self.locations = helper.initialize_location_dictionaries()
		self.comm = comm

	def save_tweet_to_db(self, data):
		result = False
		text = None
		if 'extended_tweet' in data and data['extended_tweet']:
			text = data['extended_tweet']['full_text']
		elif 'text' in data and data['text']:
			text = data['text']
		else:
			text = None
		party = self.get_party(text)
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
				print(datetime.datetime.now(), " : ", data['id_str'], " saved to tweeter database", self.comm.Get_rank())
				result = True
				if user not in self.users_db:
					self.users_db[user] = {'screen_name': data['user']['screen_name']}
			except:
				pass
		return result

	def get_party(self, text):
		parties = []
		if text:
			doc_processed = self.regex.sub('', text).strip().lower()
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

	def get_geo_location(self, data):
		loc = helper.tweet_in_australia_boundary(data, self)
		return loc
