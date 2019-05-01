import couchdb
import json
from helper import tweet_in_australia

# COUCH_SERVER = couchdb.Server("http://admin:group2@115.146.85.64:9584/")
COUCH_SERVER = couchdb.Server("http://admin:group2@115.146.84.108:9584/")
db = COUCH_SERVER['raw_twitter']

def fix_tweets():
    db = COUCH_SERVER['twitter']
    new_db = COUCH_SERVER['raw_twitter']
    print(len(db))
    for index, id in enumerate(db):
        doc = db[id]
        for i in doc:
            if i != '_id' and i != '_rev':
                try:
                    new_db[i] = doc[i]
                    print(index)
                except:
                    print(index, " already exists")
    print("done")


def get_users():
    db = COUCH_SERVER['raw_twitter']
    try:
        new_db = COUCH_SERVER.create('users_twitter')
    except:
        new_db = COUCH_SERVER['users_twitter']
    print(len(db))
    for index, id in enumerate(db):
        doc = db[id]
        screen_name = doc['user']['screen_name']
        user = doc['user']['id_str']
        if 'processed' not in doc:
            doc['processed'] = 1
            if user not in new_db:
                new_db[user] = {'count': 1, 'tweets': [doc['id_str']], 'screen_name': screen_name}
            else:
                data = new_db[user]
                data['tweets'].append(doc['id_str'])
                data['count'] = data['count'] + 1
                data['screen_name'] = screen_name
                new_db[user] = data
        else:
            data = new_db[user]
            data['screen_name'] = screen_name
            new_db[user] = data
            print("Already processed: ", screen_name)
        print(index)
        db.save(doc)


def copy_to_another_database():
    old_db = COUCH_SERVER['election_twitter']
    new_db = COUCH_SERVER['election_geo_twitter']
    rows = len(old_db)
    for index, id in enumerate(old_db):
        doc = old_db[id]
        if tweet_in_australia(doc["coordinates"], doc['geo'], doc['place']):
            try:
                new_db[doc['id_str']] = doc
            except:
                print("already there in database")
                pass
        print("left:", rows - index)


def filter_no_geo_tweets(order):
    new_db = COUCH_SERVER['twitter']
    rows = len(db)
    print("length of rows:", rows)
    count = 0
    ids = []
    for id in db:
        ids.append(id)
    ids = sorted(ids, reverse=order)
    print("Sorted the list")
    for index, id in enumerate(ids):
        doc = db[id]
        if tweet_in_australia(doc["coordinates"], doc['geo'], doc['place']):
            try:
                new_db[doc['id_str']] = doc
                count = count + 1
            except:
                pass
        if index %1000 == 0:
            print("left:", rows - index, "Inserted:", count)


def filter_no_geo_tweets_middle(order):
    new_db = COUCH_SERVER['twitter']
    rows = int(len(db) /2)
    print("length of rows:", rows)
    count = 0
    ids = []
    for id in db:
        ids.append(id)
    ids = sorted(ids, reverse=order)
    print("Sorted the list")
    for index, id in enumerate(ids[int(len(ids)/2):-1]):
        doc = db[id]
        if tweet_in_australia(doc["coordinates"], doc['geo'], doc['place']):
            try:
                new_db[doc['id_str']] = doc
                count = count + 1
            except:
                pass
        if index %1000 == 0:
            print("left:", rows - index, "Inserted:", count)


def check_no_geo_tweets():
    db = COUCH_SERVER['election_twitter']
    rows = len(db)
    print("length of rows:", rows)
    count = 0
    for index, id in enumerate(db):
        doc = db[id]
        if tweet_in_australia(doc["coordinates"], doc['geo'], doc['place']):
            count = count + 1
        if index %100 == 0:
            print(index+1, count, count/(index + 1))


def main():
    copy_to_another_database()

    return 0


if __name__ == "__main__":
    main()
