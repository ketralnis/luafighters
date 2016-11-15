import os.path
import uuid


def datafile(name, filecache={}):
    if name not in filecache:
        filecache[name] = open(os.path.join(os.path.dirname(__file__), name)).read()
    return filecache[name]


def to_base(q, alphabet):
    if q < 0:
        raise ValueError("must supply a positive integer")
    l = len(alphabet)
    converted = []
    while q != 0:
        q, r = divmod(q, l)
        converted.insert(0, alphabet[r])
    return "".join(converted) or '0'


def to36(q):
    return to_base(q, '0123456789abcdefghijklmnopqrstuvwxyz')


def to62(q):
    return to_base(q, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')


def uuid4_36():
    return to36(uuid.uuid4().int)


def uuid4_62():
    return to62(uuid.uuid4().int)
