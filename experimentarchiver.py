import imp
import os

from projectoptions import ProjectOptions
import project_utils
import git_utils

def readListFromFile(filename):
    resultList = []
    with open(filename,'r') as f:
        for line in f:
            resultList.append(line.strip())
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

class ExperimentState:
    def __init__(self, projectOptions):
        self._projectOptions = projectOptions
        self._commitHash = ''
        self._pathsToParameters = []
        self._pathsToInputData = []
        self._pathsToOutputData = []
        self._command = []
        self._environment = None
        
    def read_from_project(self):
        self._commitHash = git_utils.getGitCommitHash(self._projectOptions.path('git-path'))
        self._pathsToParameters = readListFromFile(self._projectOptions.path('parameter-list'))
        self._pathsToInputData = getPathsToInputData(self._projectOptions.path('get-input-files'))
        self._pathsToOutputData = [] # not yet implemented
        self._command = readArgumentsFromFile(self._projectOptions.path('last-command'))
        self._environment = None # not yet implemented
        
    
    def read_from_archive(self):
        pass
    
    def restore_to_project(self):
        pass
    
    def write_to_archive(self):
        pass   
        


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
    
    