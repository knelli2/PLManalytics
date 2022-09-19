from pathlib import Path
from Global import *
import os
import json


# Get the path to the name of the version file in a certain directory
def get_version_filename(directory):
    return os.path.join(directory, VERSION_FILENAME)


# Given a directory, construct a version dictionary for that directory. Note
# that there cannot be any subdirectories in a directory with a version file. If
# there are no files in that directory, return a DEFAULT_VERSION_DICT
def construct_version_dict(directory):
    version_filename = get_version_filename(directory)
    all_files = os.listdir(directory)
    if version_filename in all_files: all_files.remove(version_filename)

    versions = DEFAULT_VERSION_DICT.copy()

    if len(all_files) == 0:
        return versions

    for f in all_files:
        last_modified = Path(f).stat().st_mtime_ns()
        versions["Files"][f] = last_modified
        versions["Collective"] += last_modified

    return versions


# Read a version file from a directory into a dictionary. If there is no version
# file, return a DEFAULT_VERSION_DICT
def read_version_dict(directory):
    version_filename = get_version_filename(directory)
    if (os.path.exists(version_filename)):
        f = open(version_filename)
        return json.load(f)
    else:
        return DEFAULT_VERSION_DICT.copy()


# Return a bool on whether the version of a directory has changed by reading in
# the existing version and comparing that against the calculated version from
# the current files in the directory. If there is no version file or there are
# no files in the directory, then the version has changed
def has_version_changed(directory):
    stored_version = read_version_dict(directory)
    current_version = construct_version_dict(directory)

    if stored_version["Collective"] == 0 or current_version["Collective"] == 0:
        return True

    return stored_version["Collective"] == current_version["Collective"]


# Write a version file for a directory as a json file
def write_version(directory):
    version_filename = get_version_filename(directory)
    versions = construct_version_dict(directory)

    write_file = open(version_filename, "w+")
    json.dump(versions, write_file, indent=2)
    write_file.close()
