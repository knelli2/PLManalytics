import os
import sys
from pathlib import Path

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(SRC_DIR).parents[0]

VERSION_FILENAME = "VERSIONS"
DEFAULT_VERSION_DICT = {"Files": {}, "Collective": 0}

DB_DIR = os.path.join(ROOT_DIR, "db")

RAW_STATEMENT_DIR = os.path.join(DB_DIR, "raw_earning_statements")
CLEAN_STATEMENT_DIR = os.path.join(DB_DIR, "clean_earning_statements")
CLEAN_STATEMENT_DB = os.path.join(CLEAN_STATEMENT_DIR, "db.json")

SECRETS_FILE = os.path.join(ROOT_DIR, ".secrets")

IMAGE_DB="Images"
IMAGE_COLL="Images"
