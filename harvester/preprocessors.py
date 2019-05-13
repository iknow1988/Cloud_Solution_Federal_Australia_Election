from shapely.geometry import shape, Point, Polygon
import geopandas as gpd
import pandas as pd
import re
import nltk
from nltk import word_tokenize,sent_tokenize,wordpunct_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pika
import json


class Location:
	def __init__(self, place_name, state, geometry):
		self.place_name = place_name
		self.state = state
		self.geometry = geometry

	def give_location(self, data):
		coordinates = None
		geo = None
		place = None
		location = None
		result = None
		if "coordinates" in data and data["coordinates"]:
			result = self.check_point_intersects(data["coordinates"]["coordinates"])
		elif "geo" in data and data["geo"]:
			result = self.check_point_intersects(data["geo"]["coordinates"])
		elif 'place' in data and data['place']:
			result = self.check_bounding_box_intersects(data['place']['bounding_box'])
		elif 'user' in data and 'location' in data['user']:
			result = data['user']['location']
		else:
			result = None

		return result

	def check_point_intersects(self, coordinate):
		point = Point(coordinate[0], coordinate[1])
		if self.geometry.intersects(point):
			return self.place_name
		else:
			return None

	def check_bounding_box_intersects(self, polygon):
		s1 = shape(polygon)
		if self.geometry.intersects(s1):
			return self.place_name
		else:
			return None


class Preprocessor:

	def __init__(self, configs, boundary, tags):
		self.config = configs['APP_DATA']
		self.boundary = boundary
		x_min = float(boundary[0])
		x_max = float(boundary[2])
		y_min = float(boundary[1])
		y_max = float(boundary[3])
		self.boundary_polygon = Polygon([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]])
		self.lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
		self.stopwords = list(nltk.corpus.stopwords.words('english'))  # extend stop words if necessary
		self.stopwords.extend(['rt', 'http'])
		self.regex = re.compile('[^a-zA-Z0-9_ ]')
		self.tags = tags
		self.regex = re.compile('[^a-zA-Z0-9_ ]')
		temp = []
		for tag in self.tags:
			tag = tag.lower()
			if " " in tag or "," in tag:
				temp.extend(word_tokenize(tag))
			else:
				temp.append(tag.replace('@', ''))
		temp.extend(['rt', 'RT', 'u', 'he'])
		self.tags_tokenized = set(temp)
		self.election_seat_polygons = self.initialize_election_map()
		self.gcc_polygons = self.initialize_gcc_map()
		self.party_features = self.get_party_features()
		self.locations = self.initialize_location_dictionaries()
		self.sid = SentimentIntensityAnalyzer()
		config = configs['QUEUE']
		credentials = pika.PlainCredentials(config['queue_user'], config['queue_password'])
		parameters = pika.ConnectionParameters(config['queue_server'], config['queue_port'], '/', credentials)
		connection = pika.BlockingConnection(parameters)
		self.channel = connection.channel()
		self.channel.queue_declare(queue=config['queue_preprocess'])
		self.channel.queue_declare(queue=config['queue_savetodb'])
		self.channel.basic_consume(queue=config['queue_preprocess'], auto_ack=True, on_message_callback=self.callback)

	def check_coordinate_in_australia(self, point, boundary):
		if point['coordinates']:
			x_min = float(boundary[0])
			x_max = float(boundary[2])
			y_min = float(boundary[1])
			y_max = float(boundary[3])
			x = point['coordinates'][0]
			y = point['coordinates'][1]
			return x_min <= x <= x_max and y_min <= y <= y_max
		else:
			return False

	def check_bounding_box_in_australia(self, bounding_box, boundary_polygon):
		if bounding_box:
			s1 = shape(bounding_box)
			if s1.intersects(boundary_polygon):
				return True
			else:
				return False
		else:
			return False

	def get_city_state_country(self, location_string, locations):
		cities = locations[0]
		states = locations[0]
		countries = locations[0]
		regex2 = re.compile('[^a-zA-Z ]')
		text = regex2.sub('', str(location_string)).strip().lower()
		tokenized = set(word_tokenize(text))
		city = None
		state = None
		country = None
		common = tokenized.intersection(set(cities.keys()))
		if len(common) == 1:
			city = common.pop()
			state = cities[city]
			country = 'australia'
		else:
			common = tokenized.intersection(set(states.keys()))
			if len(common) == 1:
				state = states[common.pop()]
				country = 'australia'
			elif len(tokenized.intersection(countries)) > 0:
				country = 'australia'
		if city or state or country:
			return [city, state, country]
		else:
			return None

	def tweet_in_australia_boundary(self, data):
		seat_locations = None
		coordinates = None
		geo = None
		place = None
		user_location = None
		if "coordinates" in data:
			coordinates = data["coordinates"]
		if "geo" in data:
			geo = data['geo']
		if 'place' in data:
			place = data['place']
		if 'user' in data and 'location' in data['user']:
			user_location = data['user']['location']
		if coordinates and self.check_coordinate_in_australia(coordinates, self.boundary):
			seat_locations = []
			for election_seat in self.election_seat_polygons:
				seat_location = election_seat.give_location(data)
				if seat_location:
					seat_locations.append(seat_location)
			if len(seat_locations) == 1:
				seat_locations = seat_locations[0]
			gcc_locations = []
			for gcc in self.gcc_polygons:
				gcc_location = gcc.give_location(data)
				if gcc_location:
					gcc_locations.append(gcc_location)
			if len(gcc_locations) == 1:
				gcc_locations = gcc_locations[0]
			if len(seat_locations)>0 or len(gcc_locations)>0:
				seat_locations = [seat_locations, gcc_locations, 'australia']
			else:
				seat_locations = None
		elif geo and self.check_coordinate_in_australia(geo, self.boundary):
			seat_locations = []
			for election_seat in self.election_seat_polygons:
				seat_location = election_seat.give_location(data)
				if seat_location:
					seat_locations.append(seat_location)
			if len(seat_locations) == 1:
				seat_locations = seat_locations[0]
			gcc_locations = []
			for gcc in self.gcc_polygons:
				gcc_location = gcc.give_location(data)
				if gcc_location:
					gcc_locations.append(gcc_location)
			if len(gcc_locations) == 1:
				gcc_locations = gcc_locations[0]
			if len(seat_locations)>0 or len(gcc_locations)>0:
				seat_locations = [seat_locations, gcc_locations, 'australia']
			else:
				seat_locations = None
		elif place and self.check_bounding_box_in_australia(place['bounding_box'], self.boundary_polygon):
			seat_locations = self.get_city_state_country(place['full_name'], self.locations)
		elif user_location:
			seat_locations = self.get_city_state_country(user_location, self.locations)
		else:
			seat_locations = None

		return seat_locations

	def initialize_election_map(self):
		geodf_seats = gpd.read_file(self.config['election_map_shape_file'])
		geodf_seats.crs = {'init': 'epsg:4326'}
		seats = []
		for index, row in geodf_seats.iterrows():
			seat = Location(row['Elect_div'], row['State'], row['geometry'])
			seats.append(seat)

		return seats

	def initialize_gcc_map(self):
		geodf = gpd.read_file(self.config['gcc_map_shape_file'])
		geodf = geodf.dropna()
		geodf.crs = {'init': 'epsg:4326'}
		sa4 = []
		for index, row in geodf.iterrows():
			seat = Location(row['GCC_NAME16'], row['STE_NAME16'], row['geometry'])
			sa4.append(seat)

		return sa4

	def get_party_features(self):
		df = pd.read_csv(self.config['party_features'], encoding="ISO-8859-1")
		dictionary = {}
		for index, row in df.iterrows():
			vector = list()
			if not pd.isnull(row['party_name']):
				vector.extend([x.strip() for x in row['party_name'].split(',')])
			if not pd.isnull(row['twitter']):
				vector.extend([x.strip() for x in row['twitter'].split(',')])
			if not pd.isnull(row['abbr']):
				vector.extend([x.strip() for x in row['abbr'].split(',')])
			if not pd.isnull(row['leader']):
				vector.extend([x.strip() for x in row['leader'].split(',')])
			if not pd.isnull(row['leader_twitter']):
				vector.extend([x.strip() for x in row['leader_twitter'].split(',')])
			# if not pd.isnull(row['ideology']):
			# 	vector.extend([x.strip() for x in row['ideology'].split(',')])
			vector = [x.lower() for x in vector if not pd.isnull(x)]
			vector = [x for x in vector if not x in self.stopwords]
			dictionary[row['party_name']] = vector

		return dictionary

	def initialize_location_dictionaries(self):
		df_city_names = pd.read_csv(self.config['australia_city_names'])
		df_aurin = pd.read_csv(self.config['aurin_data_locations'])
		cities = {}

		for index, row in df_city_names.iterrows():
			cities[row['city'].lower()] = row['admin'].lower()

		for index, row in df_aurin.iterrows():
			cities[row['city'].lower()] = row['state'].lower()
			cities[row['seat'].lower()] = row['state'].lower()

		states = dict()
		states['NSW'] = 'New South Wales'
		states['QLD'] = 'Queensland'
		states['WA'] = 'Western Australia'
		states['VIC'] = 'Victoria'
		states['SA'] = 'South Australia'
		states['TAS'] = 'Tasmania'
		states['NT'] = 'Northern Territory'
		states['ACT'] = 'Australian Capital Territory'
		states['New South Wales'] = 'New South Wales'
		states['Queensland'] = 'Queensland'
		states['Western Australia'] = 'Western Australia'
		states['Victoria'] = 'Victoria'
		states['South Australia'] = 'South Australia'
		states['Tasmania'] = 'Tasmania'
		states['Northern Territory'] = 'Northern Territory'
		states['Australian Capital Territory'] = 'Australian Capital Territory'

		states = dict((k.lower(), v.lower()) for k, v in states.items())
		countries = set(['australia', 'au'])

		return [cities, states, countries]

	def lemmatize(self, word):
		lemma = self.lemmatizer.lemmatize(word, 'v')

		if lemma == word:
			lemma = self.lemmatizer.lemmatize(word, 'n')

		if lemma == word:
			lemma = self.lemmatizer.lemmatize(word, 'a')

		return lemma

	def get_processed_tweet(self, doc, tags):
		doc = re.sub("(^|\s)(@|#)(\w+)", "", doc).strip()
		new_doc = []
		for word in word_tokenize(doc):
			new_word = word.lower()
			if new_word.isalpha() and new_word not in self.stopwords:
				new_word = self.lemmatize(new_word)
				if new_word not in self.stopwords and new_word not in tags:
					new_doc.append(new_word)
		return new_doc

	def get_polarity_score(self, tweet):
		sentiment_scores = self.sid.polarity_scores(tweet)

		if sentiment_scores['compound'] < 0.0:
			sentiment_scores['sentiment'] = "Negative"
			if sentiment_scores['compound'] <= -0.5:
				sentiment_scores['intensity'] = "Strong"
			else:
				sentiment_scores['intensity'] = "Moderate"
		elif sentiment_scores['compound'] > 0.0:
			sentiment_scores['sentiment'] = "Positive"
			if sentiment_scores['compound'] >= 0.5:
				sentiment_scores['intensity'] = "Strong"
			else:
				sentiment_scores['intensity'] = "Moderate"
		else:
			sentiment_scores['sentiment'] = "Neutral"
			sentiment_scores['intensity'] = None

		return sentiment_scores

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

	def get_geo_location(self, data):
		loc = self.tweet_in_australia_boundary(data)
		return loc

	def process(self, data):
		result = False
		text = None
		if 'extended_tweet' in data and data['extended_tweet']:
			text = data['extended_tweet']['full_text']
		elif 'text' in data and data['text']:
			text = data['text']
		else:
			text = None
		if text:
			party = self.get_party(text)
			geo_data = self.get_geo_location(data)
			if geo_data and party:
				data['city'] = geo_data [0]
				data['state'] = geo_data[1]
				data['country'] = geo_data[2]
				data['party'] = party
				data['processed_text'] = self.get_processed_tweet(text, self.tags_tokenized)
				sentiment_scores = self.get_polarity_score(text)
				data['tweet_intensity'] = sentiment_scores['intensity']
				data['tweet_sentiment'] = sentiment_scores['sentiment']

				self.channel.basic_publish(exchange='', routing_key='savetodb', body=json.dumps(data))

		return result

	def callback(self, ch, method, properties, body):
		data = json.loads(body.decode('utf-8'))
		self.process(data)

	def start_processing(self):
		self.channel.start_consuming()




