import os.path

def datafile(name):
    return os.path.join(os.path.dirname(__file__), name)
