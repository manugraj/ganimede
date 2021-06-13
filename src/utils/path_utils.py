import glob
import os
import pathlib
import shutil

from fastapi import File


def paths(*args):
    return os.path.join(*args)


def paths_create(path):
    os.makedirs(path, exist_ok=True)


def paths_and_create(*args):
    v = paths(*args)
    paths_create(v)
    return v


def search(folder, extension):
    path_abs = pathlib.Path(folder).absolute()
    os.chdir(path_abs)
    return path_abs, glob.glob(f'*.{extension}')


def copy_now(from_loc, to_loc):
    return shutil.copy(from_loc, to_loc)


async def store_file_at(file: File, save_name):
    with open(save_name, "wb+") as file_object:
        file_object.write(file.file.read())


async def store_text_at(text: str, save_name):
    path = pathlib.Path(save_name)
    paths_create(path.parent.absolute())
    path.touch(exist_ok=True)
    path.write_text(data=text, encoding='utf-8')


def path_exists(path) -> bool:
    return pathlib.Path(path).exists()
