from shapely.geometry import shape, Point, Polygon
from nltk.tokenize import word_tokenize
import geopandas as gpd
import pandas as pd
from nltk import word_tokenize
import re
import nltk
regex = re.compile('[^a-zA-Z0-9_ ]')
stopwords = list(nltk.corpus.stopwords.words('english')) # extend stop words if necessary
stopwords.extend(['rt','http'])

X_MIN = 110
X_MAX = 160
Y_MIN = -44
Y_MAX = -8
AUSTRALIA = Polygon([[X_MIN, Y_MIN], [X_MIN, Y_MAX], [X_MAX, Y_MAX], [X_MAX, Y_MIN]])
locations = {'North Lismore', 'Katoomba', 'Tumby Bay', 'Traralgon',
			 'Georgetown', 'Forbes', 'Goulburn', 'Parkes', 'Geraldton', 'Innisfail',
			 'Gladstone', 'Leeton', 'Bathurst', 'Cairns', 'Carnarvon', 'Queensland',
			 'Morawa', 'Armidale', 'Smithton', 'Streaky Bay', 'Gympie South', 'Pannawonica',
			 'Seymour', 'Rockhampton', 'Sale', 'Hobart', 'Gunnedah', 'Three Springs', 'Bongaree',
			 'Townsville', 'Penola', 'Ivanhoe', 'West Tamworth', 'Ballina', 'South Australia',
			 'Longreach', 'Melbourne', 'Albany', 'Maryborough', 'Currie', 'Leonora', 'Whyalla',
			 'Gingin', 'Moree', 'Eidsvold', 'Atherton', 'Kimba', 'Nowra', 'Cranbourne', 'Northam',
			 'Port Macquarie', 'Theodore', 'Warrnambool', 'Southern Cross', 'Northern Territory',
			 'Yulara', 'Shepparton', 'Sydney', 'Byron Bay', 'Ceduna', 'Kingaroy', 'Roma', 'Victoria',
			 'Warwick', 'Cloncurry', 'Laverton', 'Clare', 'Quilpie', 'Karratha', 'South Ingham',
			 'Adelaide', 'Kingston South East', 'Canberra', 'Orange', 'Kalbarri', 'Ballarat',
			 'Exmouth', 'Kempsey', 'Swan Hill', 'Gold Coast', 'Gawler', 'Victor Harbor', 'Busselton',
			 'Mount Isa', 'Queanbeyan', 'Cowra', 'South Melbourne', 'Wallaroo', 'Hughenden', 'Hamilton',
			 'Andamooka', 'Geelong', 'Mudgee', 'Bundaberg', 'Wonthaggi', 'Port Douglas', 'Winton',
			 'Tom Price','Ravensthorpe', 'Barcaldine', 'Mount Magnet', 'Goondiwindi',
			 'Adelaide River', 'Karumba', 'Burnie', 'Cooma', 'Tweed Heads', 'Dubbo', 'Kiama',
			 'Central Coast', 'Charleville', 'Manjimup', 'Sunbury', 'Charters Towers', 'Esperance',
			 'Ulladulla', 'Kalgoorlie', 'Birdsville', 'Thargomindah', 'Western Australia', 'Weipa',
			 'McMinns Lagoon', 'Stawell', 'Pine Creek', 'Darwin', 'Young', 'Windorah', 'Dalby',
			 'Murray Bridge', 'Caloundra', 'Bourke', 'New South Wales', 'Ararat', 'Muswellbrook',
			 'Albury', 'Forster', 'Mandurah', 'Launceston', 'Queenstown', 'Meningie', 'Oatlands',
			 'Bicheno', 'Wangaratta', 'Yeppoon', 'South Grafton', 'Brisbane', 'Broome', 'Berri',
			 'Toowoomba', 'AU', 'Mildura', 'Kingoonya', 'Taree', 'Katanning', 'Alice Springs',
			 'Inverell', 'Bunbury', 'Kwinana', 'Bedourie', 'Wollongong', 'Coffs Harbour',
			 'Mount Gambier', 'Port Hedland', 'Yamba', 'Richmond North', 'Mount Barker',
			 'Camooweal', 'Emerald', 'Ouyen', 'Norseman', 'Wilcannia', 'Cowell', 'Colac',
			 'Kununurra', 'Lithgow', 'Tasmania', 'East Maitland', 'Deniliquin', 'Halls Creek',
			 'Melton', 'Katherine', 'Batemans Bay', 'Perth', 'Bowen', 'Ayr', 'Singleton', 'Bordertown',
			 'Newcastle', 'Richmond', 'Kingston Beach', 'Boulia', 'Port Pirie',
			 'Australian Capital Territory', 'Portland', 'Narrogin', 'Australia',
			 'Meekatharra', 'Biloela', 'Griffith', 'Bairnsdale East', 'Caboolture',
			 'Horsham', 'Proserpine', 'Peterborough', 'Roebourne', 'Narrabri West',
			 'Tumut', 'Newman', 'Wagga Wagga', 'Port Denison', 'Merredin', 'Wagin', 'Pambula',
			 'Onslow', 'North Mackay', 'Port Augusta West', 'Port Lincoln', 'Woomera', 'Hervey Bay',
			 'Scone', 'Cobram', 'Bendigo', 'Burketown', 'Broken Hill', 'Echuca', 'Devonport',
			 'North Scottsdale', 'Moranbah'}


def check_geo_in_australia(point, xmin = X_MIN, xmax = X_MAX, ymin = Y_MIN, ymax = Y_MAX):
	if point['coordinates']:
		x = point['coordinates'][0]
		y = point['coordinates'][1]
		return xmin <= x <= xmax and ymin <= y <= ymax
	else:
		return False


def check_bounding_box_in_australia(box, BOUNDARY_POLYGON = AUSTRALIA):
	if box:
		s1 = shape(box)
		if s1.intersects(BOUNDARY_POLYGON):
			return True
		else:
			return False
	else:
		return False


def get_city_state_country(location, cities, states, countries):
	regex2 = re.compile('[^a-zA-Z ]')
	text = regex2.sub('', str(location)).strip().lower()
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

def tweet_in_australia_boundary(data, boundary, boundary_polygon, coordinate_coordinates, geo_coordinates, bounding_box,
								location, locations_array, seat_polygons, sa4_polygons):
	locations = None
	if coordinate_coordinates and check_geo_in_australia(coordinate_coordinates, boundary[0], boundary[2],
														 boundary[1], boundary[3]):
		locations = []
		for seat in seat_polygons:
			location = seat.give_location(data)
			if location:
				locations.append(location)
		if len(locations) == 1:
			locations = locations[0]
		big_locations = []
		for big in sa4_polygons:
			big_loc = big.give_location(data)
			if big_loc:
				big_locations.append(big_loc)
		if len(big_locations) == 1:
			big_locations = big_locations[0]
		if len(locations)>0 or len(big_locations)>0:
			locations = [locations, big_locations, 'australia']
		else:
			locations = None
	elif geo_coordinates and check_geo_in_australia(geo_coordinates, boundary[0], boundary[2], boundary[1], boundary[3]):
		locations = []
		for seat in seat_polygons:
			location = seat.give_location(data)
			if location:
				locations.append(location)
		if len(locations) == 1:
			locations = locations[0]
		big_locations = []
		for big in sa4_polygons:
			big_loc = big.give_location(data)
			if big_loc:
				big_locations.append(big_loc)
		if len(big_locations) == 1:
			big_locations = big_locations[0]
		if len(locations)>0 or len(big_locations)>0:
			locations = [locations, big_locations, 'australia']
		else:
			locations = None
	elif bounding_box and check_bounding_box_in_australia(bounding_box['bounding_box'], boundary_polygon):
		locations = get_city_state_country(location, locations_array[0], locations_array[1], locations_array[2])
	elif location:
		locations = get_city_state_country(location, locations_array[0], locations_array[1], locations_array[2])
	else:
		locations = None

	return locations


def initialize_geo_map():
	geodf_seats = gpd.read_file("shape_files/COM_ELB_region.shp")
	geodf_seats.crs = {'init': 'epsg:4326'}
	seats = []
	for index, row in geodf_seats.iterrows():
		seat = Seat(row['Elect_div'], row['State'], row['geometry'])
		seats.append(seat)

	return seats


def initialize_sa_4_map():
	geodf = gpd.read_file("shape_files/GCCSA_2016_AUST.shp")
	geodf = geodf.dropna()
	geodf.crs = {'init': 'epsg:4326'}
	sa4 = []
	for index, row in geodf.iterrows():
		seat = Seat(row['GCC_NAME16'], row['STE_NAME16'], row['geometry'])
		sa4.append(seat)

	return sa4


class Seat:
	def __init__(self, Elect_div, State, geometry):
		self.Elect_div = Elect_div
		self.State = State
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
			return self.Elect_div
		else:
			return None

	def check_bounding_box_intersects(self, polygon):
		s1 = shape(polygon)
		if self.geometry.intersects(s1):
			return self.Elect_div
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
	cities = {}
	for index, row in df_city_names.iterrows():
		cities[row['city'].lower()] = row['admin'].lower()
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


