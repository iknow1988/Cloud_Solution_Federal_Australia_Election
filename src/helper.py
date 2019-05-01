from shapely.geometry import shape, Point, Polygon
# import matplotlib.pyplot as plt
# from matplotlib import patches
# import numpy as np
# from matplotlib.collections import PatchCollection

X_MIN = 110
X_MAX = 160
Y_MIN = -44
Y_MAX = -8
AUSTRALIA = Polygon([[X_MIN, Y_MIN], [X_MIN, Y_MAX], [X_MAX, Y_MAX], [X_MAX, Y_MIN]])


# def plot_polygon(polygon):
# 	fig, ax = plt.subplots(1)
#
# 	x, y = polygon.exterior.coords.xy
# 	points = np.array([x, y], np.int32).T
# 	# print(points)
# 	polygon_shape = patches.Polygon(points, linewidth=1, edgecolor='r', facecolor='none')
# 	ax.add_patch(polygon_shape)
#
# 	x, y = AUSTRALIA.exterior.coords.xy
# 	points = np.array([x, y], np.int32).T
# 	# print(points)
# 	australia_shape = patches.Polygon(points, linewidth=1, edgecolor='g', facecolor='none')
# 	ax.add_patch(australia_shape)
#
# 	plt.axis("auto")
# 	plt.show()




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


def tweet_in_australia(coordinate_coordinates, geo_coordinates, bounding_box):
	result = False
	if coordinate_coordinates and check_geo_in_australia(coordinate_coordinates):
		result = True
	elif geo_coordinates and check_geo_in_australia(geo_coordinates):
		result = True
	elif bounding_box and check_bounding_box_in_australia(bounding_box['bounding_box']):
		result = True
	else:
		return False

	return result


def tweet_in_australia_boundary(boundary, boundary_polygon, coordinate_coordinates, geo_coordinates, bounding_box):
	result = False
	if coordinate_coordinates and check_geo_in_australia(coordinate_coordinates, boundary[0], boundary[2],
														 boundary[1], boundary[3]):
		result = True
	elif geo_coordinates and check_geo_in_australia(geo_coordinates, boundary[0], boundary[2], boundary[1], boundary[3]):
		result = True
	elif bounding_box and check_bounding_box_in_australia(bounding_box['bounding_box'], boundary_polygon):
		result = True
	else:
		return False

	return result
