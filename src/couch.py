import couchdb
import json

couchserver = couchdb.Server("http://admin:group2@115.146.84.108:9584/")
new_db = couchserver['raw_twitter']

def main():
    db = couchserver['twitter']
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

if __name__ == "__main__":
	main()