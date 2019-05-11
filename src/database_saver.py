import datetime
import couchdb


class Database:

	def __init__(self, configs):
		tweet_db = None
		users_db = None
		credential_db = None
		self.couch_server = None
		try:
			connection_param = "http://%s:%s@%s:%s/" % (configs['user'], configs['password'],
														configs['ip'], configs['port'])
			self.couch_server = couchdb.Server(connection_param)
		except Exception as e:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))
			exit(0)

		try:
			tweet_db = self.couch_server.create(configs['tweet_db'])
		except Exception as e:
			if type(e).__name__ == 'PreconditionFailed':
				tweet_db = self.couch_server[configs['tweet_db']]
			elif type(e).__name__ == 'unauthorized':
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))
				exit(0)
			else:
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

		try:
			users_db = self.couch_server.create(configs['users_db'])
		except Exception as e:
			if type(e).__name__ == 'PreconditionFailed':
				users_db = self.couch_server[configs['users_db']]
			else:
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

		try:
			credential_db = self.couch_server[configs['credential_db']]
		except Exception as e:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

		if tweet_db and users_db and credential_db:
			self.tweet_db = tweet_db
			self.users_db = users_db
			self.credential_db = credential_db
			self.user = self.set_twitter_credential()
		else:
			print(datetime.datetime.now(), " : ", "Database configuration error")
			exit(0)

	def set_twitter_credential(self):
		user = None
		for index, id in enumerate(self.credential_db):
			doc = self.credential_db[id]
			if doc['in_use'] == "0":
				user = doc
				doc['in_use'] = "1"
				try:
					self.credential_db.save(doc)
					break
				except:
					print(datetime.datetime.now(), "Couldn't lock any twitter credential")
					exit(0)
		if not user:
			print(datetime.datetime.now(), " Couldn't lock any twitter credential")
			exit(0)

		return user

	def get_twitter_credential(self):
		return self.user

	def save_to_db(self, data, print_status):
		try:
			user = data['user']['id_str']
			self.tweet_db[data['id_str']] = data
			# print(data['city'], data['state'], data['country'], data['party'],
			# 	  data['processed_text'], data['tweet_intensity'], data['tweet_sentiment'])
			if print_status:
				print(datetime.datetime.now(), " : ", data['id_str'], " saved to tweeter database")
			if user not in self.users_db:
				self.users_db[user] = {'screen_name': data['user']['screen_name']}
		except Exception as e:
			if type(e).__name__ != 'ResourceConflict':
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

	def unlock_twitter_account(self):
		if self.user:
			doc = self.credential_db[self.user['_id']]
			if doc['in_use'] == "1":
				user = doc
				doc['in_use'] = "0"
				self.credential_db.save(doc)
				print(datetime.datetime.now(), " : ", user['_id'], " is unlocked")

