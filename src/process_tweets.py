import tweepy  # https://github.com/tweepy/tweepy
import json
import couchdb

# Nafis
access_token = "2680166335-Qz7Amfi0bc3gYaqnFxHmmH8BJVc10vN9mAOFuLB"
access_token_secret = "DwgayvsCmqLaEkugcsssYjf8Zqw12tfgWldq6B2FS7DkV"
consumer_key = "DzCD85X4wVcyL6AwPtFRwDxSZ"
consumer_secret = "R8oyIchRZ3Y6wpEHQRTAZ14oV3AEZIRa8eLFnMaVo543QXsFkP"

# Couchdb configure
couch = couchdb.Server('http://admin:group2@115.146.84.108:9584/')
try:
	db = couch.create('users_timeline_twitter')
except:
	db = couch['users_timeline_twitter']
tweeter_db = couch['raw_twitter']
new_db = couch['users_twitter']

def get_all_tweets(screen_name):
	# Twitter only allows access to a users most recent 3240 tweets with this method
	# authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	# initialize a list to hold all the tweepy Tweets
	alltweets = []
	# make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name=screen_name, count=200)
	# save most recent tweets
	alltweets.extend(new_tweets)
	# save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1
	# keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		# print("getting tweets before %s" % oldest)
		# all subsequent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
		# save most recent tweets
		alltweets.extend(new_tweets)
		# update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		print("...%s tweets downloaded so far" % (len(alltweets)))

	print("Downloaded all tweets of -> ", screen_name," : ", len(alltweets))

	for counter, tweet in enumerate(alltweets):
		data = tweet._json
		try:
			tweeter_db[data['id_str']] = data
			# user_data = new_db[data['user']['id_str']]
			# user_data['tweets'].append(data['id_str'])
			# user_data['count'] = user_data['count'] + 1
			# new_db[data['user']['id_str']] = user_data
		except:
			pass
			# print("Tweet exists", data['id_str'])
		if counter % 100 == 0:
			print("Left to save to database: ", len(alltweets) - counter)
	print("Saved all tweets to database")


if __name__ == '__main__':
	for index, id in enumerate(new_db):
		doc = new_db[id]
		name = doc['screen_name']
		if 'processed' not in doc:
			print(name)
			get_all_tweets(name)
			doc['processed'] = 1
			new_db.save(doc)
			print("Updated user database")
		else:
			print("already fetched data for this user:", name)
