import os
import shutil

def make_directory_if_nonexistent(path):
    if not os.path.isdir(path):
        os.mkdir(path)


#see https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
def split_all_parts(path):
    allparts = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def split_all_subpaths(path):
    subs = []
    while path:
        subs.insert(0,path)
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
        

def copy_files(fromPath,toPath,files,createDirectories=False):
    for relPath in files:
        if os.path.isabs(relPath):
            raise Exception('Only relative paths allowed')
        fromFile = os.path.join(fromPath,relPath)
        toFile = os.path.join(toPath,relPath)
        if createDirectories: 
            make_all_directories(os.path.dirname(toFile))
        shutil.copy2(fromFile, toFile)

