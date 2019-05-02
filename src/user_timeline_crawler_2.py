import tweepy  # https://github.com/tweepy/tweepy
import json
import couchdb
from helper import tweet_in_australia

# Couchdb configure
couch = couchdb.Server('http://admin:group2@115.146.84.108:9584/')
tweeter_db = couch['election_geo_twitter']
user_db = couch['followers']


def get_all_tweets(screen_name):
	# Twitter only allows access to a users most recent 3240 tweets with this method
	# authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	# initialize a list to hold all the tweepy Tweets
	all_tweets = []
	# make initial request for most recent tweets (200 is the maximum allowed count)
	try:
		new_tweets = api.user_timeline(user_id=screen_name, count=200)
		# save most recent tweets
		all_tweets.extend(new_tweets)
		# save the id of the oldest tweet less one
		oldest = all_tweets[-1].id - 1
	except:
		new_tweets = []
		pass
	# keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		# print("getting tweets before %s" % oldest)
		# all subsequent requests use the max_id param to prevent duplicates
		try:
			new_tweets = api.user_timeline(user_id=screen_name, count=200, max_id=oldest)
		except:
			pass
		# save most recent tweets
		all_tweets.extend(new_tweets)
		# update the id of the oldest tweet less one
		oldest = all_tweets[-1].id - 1
		# print("...%s tweets downloaded so far" % (len(all_tweets)))
		if len(all_tweets)>3000:
			break

	print("Downloaded all tweets of -> ", screen_name," : ", len(all_tweets))
	count = 0

	for counter, tweet in enumerate(all_tweets):
		data = tweet._json
		if tweet_in_australia(data["coordinates"], data['geo'], data['place']):
			try:
				tweeter_db[data['id_str']] = data
				count = count + 1
			except:
				pass
				# print("Tweet in database")
		# if count and counter % 100 == 0:
		# 	print("Left to save to database: ", len(all_tweets) - counter)
	if count:
		print("Saved %s tweets to database" % count, "for user:", screen_name)


if __name__ == '__main__':
	rows = len(user_db)
	print(rows)
	for index, id in enumerate(user_db):
		doc = user_db[id]
		name = id
		print(name)
		if doc['processed'] == 0:
			get_all_tweets(name)
			doc['processed'] = 1
			try:
				user_db.save(doc)
				print("Updated %s database" %name)
			except:
				print("%s database update error" % name)
		else:
			print("User already processed")
		print("left:", rows - index)
