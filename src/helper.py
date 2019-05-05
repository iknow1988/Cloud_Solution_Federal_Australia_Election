from shapely.geometry import shape, Point, Polygon
from nltk.tokenize import word_tokenize
import geopandas as gpd

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


def tweet_in_australia_boundary(boundary, boundary_polygon, coordinate_coordinates, geo_coordinates, bounding_box,
								location):
	result = False
	if coordinate_coordinates and check_geo_in_australia(coordinate_coordinates, boundary[0], boundary[2],
														 boundary[1], boundary[3]):
		result = True
	elif geo_coordinates and check_geo_in_australia(geo_coordinates, boundary[0], boundary[2], boundary[1], boundary[3]):
		result = True
	elif bounding_box and check_bounding_box_in_australia(bounding_box['bounding_box'], boundary_polygon):
		result = True
	elif location:
		tweet_locations = set(word_tokenize(location))
		common = locations.intersection(tweet_locations)
		if len(common) > 0:
			result = True
	else:
		result = False

	return result


def initialize_geo_map():
	geodf_seats = gpd.read_file("shape/COM_ELB_region.shp")
	geodf_seats.crs = {'init': 'epsg:4326'}
	seats = []
	for index, row in geodf_seats.iterrows():
		seat = Seat(row['Elect_div'], row['State'], row['geometry'])
		seats.append(seat)

	return seats


def initialize_sa_4_map():
	geodf = gpd.read_file("australia/GCCSA_2016_AUST.shp")
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



