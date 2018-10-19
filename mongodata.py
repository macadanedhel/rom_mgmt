import ConfigParser
import datetime
import pymongo

class mongodata:
    ENVCONFIG = "config/env.ini"
    EnvConfig = ConfigParser.ConfigParser()
    Config = ConfigParser.ConfigParser()
    EnvConfig.read(ENVCONFIG)
    DATETIME = ""
    BBDD = ""

    def __init__(self):
        self.EnvConfig = ConfigParser.ConfigParser()
        self.EnvConfig.read(self.ENVCONFIG)
        self.DATETIME = str(datetime.datetime.isoformat(datetime.datetime.now()))
        host = self.EnvConfig.get('mongodb', 'ip')
        port = int(self.EnvConfig.get('mongodb', 'port'))
        client = pymongo.MongoClient(host, port)
        self.BBDD = client.twitter
        args={ "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["friends_count", "followers_count", "listed_count", "statuses_count", "favourites_count"],
            "properties": {
                "friends_count": {
                    "bsonType": "long"
                },
                "followers_count": {
                    "bsonType": "long"
                },
                "listed_count": {
                    "bsonType": "long"
                },
                "statuses_count": {
                    "bsonType": "long"
                },
                "favourites_count": {
                    "bsonType": "long"
                }
            }
        }}
        }
        #self.BBDD.create_collection("users",**args)
    def insert_many_users (self,  ALLDATA):
        try:
            self.BBDD.users.insert_many(ALLDATA, ordered=False).inserted_ids
        except pymongo.errors.BulkWriteError as e:
                    #print("Error:{0}").format(e.details['writeErrors'])
                    print "Error, duplicate data"


