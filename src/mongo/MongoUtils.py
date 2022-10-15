import os
import sys

import pymongo

from src.Global import SECRETS_FILE


def get_client():
  if not os.path.exists(SECRETS_FILE):
      print(
          "Could not find a '.secrets' file in the root of this repository. "
          "Please add it. It should have the following format:"
          "\n\nMONGO_USERNAME=myusername\nMONGO_PASSWORD=mypassword\n\n"
          "where 'myusername' and 'mypassword' are to your PLManalytics account "
          "on MongoDB."
      )
      sys.exit()
  
  mongo_username = ""
  mongo_password = ""

  with open(SECRETS_FILE, "r") as f:
    secrets = f.read().split("\n")
    mongo_username=secrets[0].split("=")[-1]
    mongo_password=secrets[1].split("=")[-1]
  
  uri = f"mongodb+srv://{mongo_username}:{mongo_password}" \
    "@plmanalytics.uwia1aq.mongodb.net/?retryWrites=true&w=majority"

  client = pymongo.MongoClient(uri)

  mongo_username = ""
  mongo_password = ""
  secrets = []

  return client

def get_database(client, database_name):
  return client[database_name]

def get_collection(database, collection_name):
  return database[collection_name]

def collection_contains_id(collection, id):
  return collection.find_one({"_id": id}) != None
