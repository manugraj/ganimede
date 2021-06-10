import os


def paths(*args):
    return os.path.join(*args)


def paths_create(path):
    os.makedirs(path, exist_ok=True)


def paths_and_create(*args):
    v = paths(*args)
    paths_create(v)
    return v
