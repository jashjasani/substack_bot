import pymongo
import os
from dotenv import load_dotenv
from mongoengine import connect, Document, StringField, IntField, DateTimeField
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATA_BASE_NAME = "Users"


class User(Document):
    user_id = IntField(required=True)
    username = StringField()
    name = StringField()
    start_date = DateTimeField(required=True)
    type = StringField(required=True)
    channel_id = StringField(required=True)
    email = StringField(required=True)
    end_date = DateTimeField(required=True)



def addUser(data):
    try: 
        connect("Users", host=MONGO_URI,  alias="default")
        document = User(**data)
        document.save()
        print("Document saved successfully!")
    except Exception as e:
        print(f"Error saving document: {e}")


def findUser(collection_name, user_id):
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client.get_database(DATA_BASE_NAME)
        collection = db[collection_name]
        
        
        result = collection.find_one({ "user_id" : user_id })

        if result:
            return result
    except Exception as e:
        print(e)    

data = {
            "user_id" : 1098,
            "username" : "jacube",
            "name" : "Jash",
            "type" : "type",
            "channel_id" : "channel_id",
            "email" : "email",
            "start_date" : datetime.now().date(),
            "end_date" : datetime.now().date()
        }

print(findUser("user", 198))