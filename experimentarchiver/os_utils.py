import os
import shutil


def make_directory_if_nonexistent(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def split_all_parts(path):
    """see https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html"""
    allparts = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:   # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def split_all_subpaths(path):
    subs = []
    while path:
        subs.insert(0, path)
        parts = os.path.split(path)
        if path == parts[0]:
            break
        path = parts[0]
    return subs


def make_all_directories(path):
    if os.path.isabs(path):
        raise Exception('Only relative paths allowed')
    for sub in split_all_subpaths(path):
        make_directory_if_nonexistent(sub)
        

def copy_files(from_path, to_path, files, create_directories=False):
    for relPath in files:
        if os.path.isabs(relPath):
            raise Exception('Only relative paths allowed')
        from_file = os.path.join(from_path, relPath)
        to_file = os.path.join(to_path, relPath)
        if create_directories:
            make_all_directories(os.path.dirname(to_file))
        shutil.copy2(from_file, to_file)
