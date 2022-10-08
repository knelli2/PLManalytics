import pymongo
from Global import *

def get_client():
  set_secrets()
  return pymongo.MongoClient(
      f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}"
      "@plmanalytics.uwia1aq.mongodb.net/$retryWrites=true&w=majority"
  )
