import os
import hashlib
import json
import subprocess
import imp

from projectoptions import ProjectOptions
from archiveoptions import ArchiveOptions
import experimentarchiver.os_utils as os_utils
import experimentarchiver.git_utils as git_utils

def computeFileHash(fileName, hashAlgorithm):
    fileHash = hashlib.new(hashAlgorithm)
    
    bufferSize = 64 * pow(2,10) 
    fileToHash = open(fileName,'rb')
    while True:
        chunk = fileToHash.read(bufferSize)
        if (not chunk):
            break
        fileHash.update(chunk)
    fileToHash.close()
        
    return "{0}".format(fileHash.hexdigest())

def readListFromFile(filename):
    resultList = []
    with open(filename,'r') as f:
        resultList = [line.strip() for line in f]
    return resultList


def getPathsToInputData(pathToScriptFile):
    importedModule = imp.load_source('tmp_script_module',pathToScriptFile)
    savePath = os.getcwd()
    pathList = []
    try:
        scriptPath = os.path.dirname(pathToScriptFile)
        os.chdir(scriptPath)
        pathList = importedModule.getFilesToHash()
    finally:
        os.chdir(savePath)
    return pathList

def read_json(filename):
    with open(filename,'r') as f:
        data = json.load(f)
    return data


def write_json(data,filename):
    with open(filename,'w') as f:
        json.dump(data,f)

class ExperimentState:
    def __init__(self, projectOptions,archiveOptions):
        self._projectOptions = projectOptions
        self._archiveOptions = archiveOptions
        self._commitHash = ''
        self._pathsToParameters = []
        self._inputData = []
        self._pathsToOutputData = []
        self._command = []
        self._environment = None
        
    def _hash_input_data(self):
        relativePathsToInputData = getPathsToInputData(self._projectOptions.path('get-input-files'))
        hashAlgorithm =  self._projectOptions.option('hash-algorithm')        
        data = []
        for relPath in relativePathsToInputData:
            absPath = os.path.join(self._projectOptions.path('input-data-path'),relPath)
            fileHash = computeFileHash(absPath,hashAlgorithm)
            data.append((relPath, hashAlgorithm, fileHash))
        return data

    def _verify_hashes(self):
        for (relPath, hashAlgorithm, storedHash) in self._inputData:
            absPath = os.path.join(self._projectOptions.path('input-data-path'),relPath)
            computedHash = computeFileHash(absPath,hashAlgorithm)
            if (storedHash != computedHash):
                raise Exception("The stored and computed {0} hashes for the file {1} differ: {2} != {3}".format(hashAlgorithm,absPath,storedHash,computedHash))

    def _build_project(self):
        buildCommand = self._projectOptions.option('build-command').strip().split()
        savePath = os.getcwd()
        try:
            os.chdir(self._projectOptions.path('build-path'))
            subprocess.check_call(buildCommand)
        finally:
            os.chdir(savePath)
            
    def get_command(self):
        return self._command
    
    def update_command_status(self):
        self._command = read_json(self._projectOptions.path('last-command'))
        

    def read_from_project(self):
        self._commitHash = git_utils.get_git_commit_hash(self._projectOptions.path('git-path'))
        self._pathsToParameters = readListFromFile(self._projectOptions.path('parameter-list'))
        repoIsClean = git_utils.is_git_repo_clean(self._projectOptions.path('git-path'),
                                                  self._projectOptions.path('top-path'),
                                                  self._pathsToParameters)
        if not repoIsClean:
            raise Exception('The git repository contains unstaged or uncommitted changes')
        self._inputData = self._hash_input_data()
        self._pathsToOutputData = [] # not yet implemented
        self._command = read_json(self._projectOptions.path('last-command'))
        self._environment = None # not yet implemented


    def restore_to_project(self):
        pathsToParameters = readListFromFile(self._projectOptions.path('parameter-list'))
        repoIsClean = git_utils.is_git_repo_clean(self._projectOptions.path('git-path'),
                                                  self._projectOptions.path('top-path'),
                                                  pathsToParameters)
        if not repoIsClean:
            raise Exception('The git repository contains unstaged or uncommitted changes')
        git_utils.checkout_git_commit(self._projectOptions.path('git-path'), self._commitHash)
        os_utils.copy_files(self._archiveOptions.path('parameter-path'),
                            self._projectOptions.path('top-path'),
                            self._pathsToParameters,
                            create_directories=False)
        # nothing to do for input data
        # output data not implemented
        write_json(self._command, self._projectOptions.path('last-command'))
        # environment not implemented 
        if self._projectOptions.option('do-build'):
            self._build_project()


    def read_from_archive(self):
        self._commitHash = read_json(self._archiveOptions.path('commit-hash'))
        self._pathsToParameters = read_json(self._archiveOptions.path('parameter-list'))
        self._inputData = read_json(self._archiveOptions.path('input-files')) 
        self._verify_hashes()
        self._pathsToOutputData = [] # not yet implemented
        self._command = read_json(self._archiveOptions.path('last-command'))
        self._environment = None # not yet implemented


    def write_to_archive(self):
        os_utils.make_directory_if_nonexistent(self._archiveOptions.path('archive-path'))
        os_utils.make_directory_if_nonexistent(self._archiveOptions.path('experiment-path'))
        write_json(self._commitHash, self._archiveOptions.path('commit-hash')) 
        os_utils.make_directory_if_nonexistent(self._archiveOptions.path('parameter-path'))
        write_json(self._pathsToParameters,self._archiveOptions.path('parameter-list'))
        os_utils.copy_files(self._projectOptions.path('top-path'),
                            self._archiveOptions.path('parameter-path'),
                            self._pathsToParameters,
                            create_directories=True)
        write_json(self._inputData,self._archiveOptions.path('input-files'))
        # output data not yet implemented
        write_json(self._command,self._archiveOptions.path('last-command'))
        #environment not yet implemented