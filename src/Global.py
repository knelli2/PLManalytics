import os
from pathlib import Path
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(SRC_DIR).parents[0]

VERSION_FILENAME = "VERSIONS"
DEFAULT_VERSION_DICT = {"Files": {}, "Collective": 0}

DB_DIR = os.path.join(ROOT_DIR, "db")

RAW_STATEMENT_DIR = os.path.join(DB_DIR, "raw_earning_statements")
CLEAN_STATEMENT_DIR = os.path.join(DB_DIR, "clean_earning_statements")
CLEAN_STATEMENT_DB = os.path.join(CLEAN_STATEMENT_DIR, "db.json")

SECRETS_FILE = os.path.join(ROOT_DIR, ".secrets")
MONGO_USERNAME=""
MONGO_PASSWORD=""
SECRETS_SET=False

def set_secrets():
  if SECRETS_SET:
    return

  if not os.path.exists(SECRETS_FILE):
      print(
          "Could not find a '.secrets' file in the root of this repository. "
          "Please add it. It should have the following format:"
          "\n\nMONGO_USERNAME=myusername\nMONGO_PASSWORD=mypassword\n\n"
          "where 'myusername' and 'mypassword' are to your PLManalytics account "
          "on MongoDB."
      )
      sys.exit()

  with open(SECRETS_FILE, "r") as f:
    secrets = f.read().split("\n")
    MONGO_USERNAME=secrets[0]
    MONGO_PASSWORD=secrets[1]
  
  SECRETS_SET=True
