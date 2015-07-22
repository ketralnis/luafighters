import os.path

def datafile(name):
    return os.path.join(os.path.dirname(__file__), name)

def coroutine(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start