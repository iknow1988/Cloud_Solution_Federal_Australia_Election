import couchdb
import json

couchserver = couchdb.Server("http://admin:group2@115.146.84.108:9584/")

def fix_tweets():
    db = couchserver['twitter']
    new_db = couchserver['raw_twitter']
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
    db = couchserver['raw_twitter']
    try:
        new_db = couchserver.create('users_twitter')
    except:
        new_db = couchserver['users_twitter']
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


def copy_to_database():
    old_db = couchserver['users_timeline_twitter']
    new_db = couchserver['raw_twitter']
    rows = len(old_db)
    for index, id in enumerate(old_db):
        doc = old_db[id]
        try:
            new_db[doc['id_str']] = doc
        except:
            print("already there in database")
            pass
        print("left:", rows - index)


def main():
    copy_to_database()

    return 0

if __name__ == "__main__":
	main()