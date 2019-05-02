import time
import tweepy
import couchdb
import pandas as pd
import datetime

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True,
                 retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]), compression=True)

COUCH_SERVER = couchdb.Server("http://admin:group2@115.146.84.108:9584/")


def get_followers(party):
   ids = []
   for page in tweepy.Cursor(api.followers_ids, screen_name=party).pages():
      ids.extend(page)
      print(datetime.datetime.now(), " : ", party," : Downloaded: " , len(page))
      add_followers(page)
      if len(ids)>50000:
         break
   print(datetime.datetime.now(), " : Ended for ", party, len(ids))


def add_followers(followers):
   count = 0
   try:
      followers_db = COUCH_SERVER.create('followers')
   except:
      followers_db = COUCH_SERVER['followers']
   for index, id in enumerate(followers):
      if not str(id) in followers_db:
         followers_db[str(id)] = {'processed': 0}
         count = count + 1
   print(datetime.datetime.now(), " : ","saved ", count, "followers to database")


def main():
   df = pd.read_csv('australia.csv', encoding="ISO-8859-1")
   party_pages = df.twitter.values
   for party in party_pages:
      get_followers(party)

if __name__ == "__main__":
	main()


