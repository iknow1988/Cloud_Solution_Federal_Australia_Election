from shapely.geometry import shape, Point, Polygon
from nltk.tokenize import word_tokenize
import geopandas as gpd
import pandas as pd
from nltk import word_tokenize
import re
import nltk
from nltk import word_tokenize,sent_tokenize,wordpunct_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# create object - pretrained basic model based on lexicons
sid = SentimentIntensityAnalyzer()
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

# pre process documents removing stop words, non alpha and lemmatizing
stopwords = list(nltk.corpus.stopwords.words('english'))  # extend stop words if necessary
stopwords.extend(['rt', 'http'])
regex = re.compile('[^a-zA-Z0-9_ ]')
stopwords = list(nltk.corpus.stopwords.words('english')) # extend stop words if necessary
stopwords.extend(['rt','http'])


def check_coordinate_in_australia(point, boundary):
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


def check_bounding_box_in_australia(bounding_box, boundary_polygon):
	if bounding_box:
		s1 = shape(bounding_box)
		if s1.intersects(boundary_polygon):
			return True
		else:
			return False
	else:
		return False


def get_city_state_country(location_string, locations):
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


def tweet_in_australia_boundary(data, harvester):
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
	if coordinates and check_coordinate_in_australia(coordinates, harvester.boundary):
		seat_locations = []
		for election_seat in harvester.election_seat_polygons:
			seat_location = election_seat.give_location(data)
			if seat_location:
				seat_locations.append(seat_location)
		if len(seat_locations) == 1:
			seat_locations = seat_locations[0]
		gcc_locations = []
		for gcc in harvester.gcc_polygons:
			gcc_location = gcc.give_location(data)
			if gcc_location:
				gcc_locations.append(gcc_location)
		if len(gcc_locations) == 1:
			gcc_locations = gcc_locations[0]
		if len(seat_locations)>0 or len(gcc_locations)>0:
			seat_locations = [seat_locations, gcc_locations, 'australia']
		else:
			seat_locations = None
	elif geo and check_coordinate_in_australia(geo, harvester.boundary):
		seat_locations = []
		for election_seat in harvester.election_seat_polygons:
			seat_location = election_seat.give_location(data)
			if seat_location:
				seat_locations.append(seat_location)
		if len(seat_locations) == 1:
			seat_locations = seat_locations[0]
		gcc_locations = []
		for gcc in harvester.gcc_polygons:
			gcc_location = gcc.give_location(data)
			if gcc_location:
				gcc_locations.append(gcc_location)
		if len(gcc_locations) == 1:
			gcc_locations = gcc_locations[0]
		if len(seat_locations)>0 or len(gcc_locations)>0:
			seat_locations = [seat_locations, gcc_locations, 'australia']
		else:
			seat_locations = None
	elif place and check_bounding_box_in_australia(place['bounding_box'], harvester.boundary_polygon):
		seat_locations = get_city_state_country(place['full_name'], harvester.locations)
	elif user_location:
		seat_locations = get_city_state_country(user_location, harvester.locations)
	else:
		seat_locations = None

	return seat_locations


def initialize_election_map():
	geodf_seats = gpd.read_file("shape_files/COM_ELB_region.shp")
	geodf_seats.crs = {'init': 'epsg:4326'}
	seats = []
	for index, row in geodf_seats.iterrows():
		seat = Location(row['Elect_div'], row['State'], row['geometry'])
		seats.append(seat)

	return seats


def initialize_gcc_map():
	geodf = gpd.read_file("shape_files/GCCSA_2016_AUST.shp")
	geodf = geodf.dropna()
	geodf.crs = {'init': 'epsg:4326'}
	sa4 = []
	for index, row in geodf.iterrows():
		seat = Location(row['GCC_NAME16'], row['STE_NAME16'], row['geometry'])
		sa4.append(seat)

	return sa4


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


def get_party_features():
	df = pd.read_csv('csv_files/political_party_attributes.csv', encoding="ISO-8859-1")
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
		vector = [x for x in vector if not x in stopwords]
		dictionary[row['party_name']] = vector

	return dictionary


def initialize_location_dictionaries():
	df_city_names = pd.read_csv('csv_files/australia_city_names.csv')
	df_aurin = pd.read_csv('csv_files/aurin_location.csv')
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


def lemmatize(word):
	lemma = lemmatizer.lemmatize(word, 'v')

	if lemma == word:
		lemma = lemmatizer.lemmatize(word, 'n')

	if lemma == word:
		lemma = lemmatizer.lemmatize(word, 'a')

	return lemma


def get_processed_tweet(doc):
	new_doc = []
	for word in word_tokenize(doc):
		new_word = word.lower()
		if new_word.isalpha() and new_word not in stopwords:
			new_word = lemmatize(new_word)
			if new_word not in stopwords:
				new_doc.append(new_word)
	return new_doc


def get_polarity_score(tweet):
	sentiment_scores = sid.polarity_scores(tweet)

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

