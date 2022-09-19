from pathlib import Path


# Get the directory that a file is in
def get_directory(filename):
    return Path(filename).parents[0]
