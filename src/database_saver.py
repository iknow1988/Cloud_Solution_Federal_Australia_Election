import datetime
import couchdb
import pika
import json


class Database:

	def __init__(self, configs):
		tweet_db = None
		users_db = None
		credential_db = None
		self.couch_server = None
		database_config = configs['COUCHDB']
		queue_config = configs['QUEUE']
		try:
			connection_param = "http://%s:%s@%s:%s/" % (database_config['user'], database_config['password'],
														database_config['ip'], database_config['port'])
			self.couch_server = couchdb.Server(connection_param)
		except Exception as e:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))
			exit(0)

		try:
			tweet_db = self.couch_server.create(database_config['tweet_db'])
		except Exception as e:
			if type(e).__name__ == 'PreconditionFailed':
				tweet_db = self.couch_server[database_config['tweet_db']]
			elif type(e).__name__ == 'unauthorized':
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))
				exit(0)
			else:
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

		try:
			users_db = self.couch_server.create(database_config['users_db'])
		except Exception as e:
			if type(e).__name__ == 'PreconditionFailed':
				users_db = self.couch_server[database_config['users_db']]
			else:
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

		try:
			credential_db = self.couch_server[database_config['credential_db']]
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

		credentials = pika.PlainCredentials(queue_config['queue_user'], queue_config['queue_password'])
		parameters = pika.ConnectionParameters(queue_config['queue_server'], queue_config['queue_port'], '/', credentials)
		connection = pika.BlockingConnection(parameters)
		self.channel = connection.channel()
		self.channel.queue_declare(queue=queue_config['queue_savetodb'])
		self.channel.basic_consume(queue=queue_config['queue_savetodb'], auto_ack=True, on_message_callback=self.callback)


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

	def save_to_db(self, data, print_status = True):
		result = False
		try:
			user = data['user']['id_str']
			self.tweet_db[data['id_str']] = data
			result = True
			if print_status:
				print(datetime.datetime.now(), " : ", data['id_str'], " saved to tweeter database")
			if user not in self.users_db:
				self.users_db[user] = {'screen_name': data['user']['screen_name']}
		except Exception as e:
			if type(e).__name__ != 'ResourceConflict':
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				print(datetime.datetime.now(), " : ", template.format(type(e).__name__, e.args))

		return result

	def unlock_twitter_account(self):
		if self.user:
			doc = self.credential_db[self.user['_id']]
			if doc['in_use'] == "1":
				user = doc
				doc['in_use'] = "0"
				self.credential_db.save(doc)
				print(datetime.datetime.now(), " : ", user['_id'], " is unlocked")

	def callback(self, ch, method, properties, body):
		data = json.loads(body.decode('utf-8'))
		self.save_to_db(data)

	def start_saving(self):
		self.channel.start_consuming()

