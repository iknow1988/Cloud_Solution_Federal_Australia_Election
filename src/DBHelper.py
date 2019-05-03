import couchdb
import json
import pandas as pd
from collections import Counter, defaultdict
import csv


class DBHelper:
	def __init__(self, db_name):
		couch_server = couchdb.Server("http://admin:group2@115.146.84.108:9584/")
		self.db = couch_server[db_name]

	def get_document_count(self):
		return len(self.db)

	def get_hashtag_counts(self):
		view = self.db.view('_design/views/_view/all_hashtags', reduce=True, group=True)
		self.write_to_csv(view, 'hashtag_counts.csv')

	def get_leader_mentions_counts(self):
		view = self.db.view('_design/views/_view/leader_mentions', reduce=True, group=True)
		self.write_to_csv(view, 'leader_mention_counts.csv')

	def get_party_mentions_counts(self):
		view = self.db.view('_design/views/_view/party_mentions', reduce=True, group=True)
		self.write_to_csv(view,'party_mention_counts.csv')

	def write_to_csv(self, view, name):
		with open(name, 'w') as file:
			file.write("key, value")
			file.write('\n')
			for item in view:
				file.write(str(item.key)+", "+ str(item.value))
				file.write('\n')


def main():
	db_helper = DBHelper('election_geo_twitter')
	# hashtag count takes time
	db_helper.get_hashtag_counts()
	db_helper.get_leader_mentions_counts()
	db_helper.get_party_mentions_counts()
	print("done")
	return 0


if __name__ == "__main__":
	main()
