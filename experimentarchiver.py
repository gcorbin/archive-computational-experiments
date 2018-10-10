import imp
import os
import json
import shutil

from projectoptions import ProjectOptions
from archiveoptions import ArchiveOptions
import project_utils
import git_utils

def readListFromFile(filename):
    resultList = []
    with open(filename,'r') as f:
        resultList = [line.strip() for line in f]
    return resultList

def readArgumentsFromFile(filename):
    args = []
    with open(filename,'r') as f:
        args = f.readline().strip('\n').strip(' ').split(' ')
    return args

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

def make_directory_if_nonexistent(path):
    if not os.path.isdir(path):
        os.mkdir(path)

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
        
    def hash_input_data(self):
        relativePathsToInputData = getPathsToInputData(self._projectOptions.path('get-input-files'))
        hashAlgorithm =  self._projectOptions.option('hash-algorithm')        
        data = []
        for relPath in relativePathsToInputData:
            absPath = os.path.join(self._projectOptions.path('input-data-path'),relPath)
            fileHash = project_utils.computeFileHash(absPath,hashAlgorithm)
            data.append((relPath, hashAlgorithm, fileHash))
        return data

    
    #def read_stored_input_data(self):
        #data = []
        #with open(self._archiveOptions.path('input-files'),'r') as f:
            #data = json.load(f)
        ##todo: check data for correctness
        #return data
            
    #def store_input_data(self,data):
        #with open(self._archiveOptions.path('input-files'),'w') as f:
            #json.dump(data,f)
            
            
    def verify_hashes(self):
        for (relPath, hashAlgorithm, storedHash) in self._inputData:
            absPath = os.path.join(self._projectOptions.path('input-data-path'),relPath)
            computedHash = project_utils.computeFileHash(absPath,hashAlgorithm)
            if (storedHash != computedHash):
                raise Exception("The stored and computed {0} hashes for the file {1} differ: {2} != {3}".format(hashAlgorithm,absPath,storedHash,computedHash))
        
            

    def read_from_project(self):
        self._commitHash = git_utils.getGitCommitHash(self._projectOptions.path('git-path'))
        self._pathsToParameters = readListFromFile(self._projectOptions.path('parameter-list'))
        self._inputData = self.hash_input_data()
        self._pathsToOutputData = [] # not yet implemented
        self._command = readArgumentsFromFile(self._projectOptions.path('last-command'))
        self._environment = None # not yet implemented
        
    def restore_to_project(self):
        pass

    def read_from_archive(self):
        self._commitHash = git_utils.readCommitHashFromFile(self._archiveOptions.path('commit-hash'))
        self._pathsToParameters = read_json(self._archiveOptions.path('parameter-list'))
        self._inputData = read_json(self._archiveOptions.path('input-files')) 
        self.verify_hashes()
        self._pathsToOutputData = [] # not yet implemented
        self._command = readArgumentsFromFile(self._archiveOptions.path('last-command'))
        self._environment = None # not yet implemented
    
    def write_to_archive(self):
        make_directory_if_nonexistent(self._archiveOptions.path('archive-path'))
        make_directory_if_nonexistent(self._archiveOptions.path('experiment-path'))
        git_utils.writeCommitHashToFile(self._archiveOptions.path('commit-hash'),self._commitHash) 
        make_directory_if_nonexistent(self._archiveOptions.path('parameter-path'))
        write_json(self._pathsToParameters,self._archiveOptions.path('parameter-list'))
        for path in self._pathsToParameters:
            fromFile = os.path.join(self._projectOptions.path('top-path'),path)
            toFile = os.path.join(self._archiveOptions.path('parameter-path'),
                                          path)
            make_all_directories(os.path.dirname(toFile))
            shutil.copy2(fromFile, toFile)
        write_json(self._inputData,self._archiveOptions.path('input-files'))
        # output data not yet implemented
        write_json(self._command,self._archiveOptions.path('last-command'))
        #environment not yet implemented
        
class ExperimentArchiver:
    
    def __init__(self, archiverOptions, projectOptions):
        self.archiverOptions = archiverOptions
        self.projectOptions = projectOptions
        self.logger = None
    
    def run_and_record(self,command):
        pass
    
    def archive(self):
        pass
    
    def restore(self):
        pass
    
    def run_and_archive(self):
        pass
    
    def restore_and_run(self):
        pass
    
    