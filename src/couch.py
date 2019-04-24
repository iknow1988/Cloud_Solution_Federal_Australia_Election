import couchdb

couchserver = couchdb.Server("http://115.146.85.64:9584/")

for dbname in couchserver:
    print(dbname)

print("Done")