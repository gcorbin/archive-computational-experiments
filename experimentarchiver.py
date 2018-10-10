import imp
import os
import json
import shutil
import subprocess

from projectoptions import ProjectOptions
from archiveoptions import ArchiveOptions
import project_utils
import git_utils

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


def copy_files(fromPath,toPath,files,createDirectories=False):
    for relPath in files:
        if os.path.isabs(relPath):
            raise Exception('Only relative paths allowed')
        fromFile = os.path.join(fromPath,relPath)
        toFile = os.path.join(toPath,path)
        if createDirectories: 
            make_all_directories(os.path.dirname(toFile))
        shutil.copy2(fromFile, toFile)


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

    def verify_hashes(self):
        for (relPath, hashAlgorithm, storedHash) in self._inputData:
            absPath = os.path.join(self._projectOptions.path('input-data-path'),relPath)
            computedHash = project_utils.computeFileHash(absPath,hashAlgorithm)
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

    def read_from_project(self):
        self._commitHash = git_utils.getGitCommitHash(self._projectOptions.path('git-path'))
        self._pathsToParameters = readListFromFile(self._projectOptions.path('parameter-list'))
        self._inputData = self.hash_input_data()
        self._pathsToOutputData = [] # not yet implemented
        self._command = read_json(self._projectOptions.path('last-command'))
        self._environment = None # not yet implemented


    def restore_to_project(self):
        git_utils.checkoutGitCommit(self._projectOptions.path('git'),self._commitHash)
        copy_files(self._archiveOptions.path('parameter-path'),
                   self._projectOptions.path('top-path'),
                   self._pathsToParameters,
                   createDirectories=False)
        # nothing to do for input data
        # output data not implemented
        write_json(self._command, self._projectOptions.path('last-command'))
        # environment not implemented 
        if self._projectOptions.option('do-build'):
            self._build_project()


    def read_from_archive(self):
        self._commitHash = git_utils.readCommitHashFromFile(self._archiveOptions.path('commit-hash'))
        self._pathsToParameters = read_json(self._archiveOptions.path('parameter-list'))
        self._inputData = read_json(self._archiveOptions.path('input-files')) 
        self.verify_hashes()
        self._pathsToOutputData = [] # not yet implemented
        self._command = read_json(self._archiveOptions.path('last-command'))
        self._environment = None # not yet implemented


    def write_to_archive(self):
        make_directory_if_nonexistent(self._archiveOptions.path('archive-path'))
        make_directory_if_nonexistent(self._archiveOptions.path('experiment-path'))
        git_utils.writeCommitHashToFile(self._archiveOptions.path('commit-hash'),self._commitHash) 
        make_directory_if_nonexistent(self._archiveOptions.path('parameter-path'))
        write_json(self._pathsToParameters,self._archiveOptions.path('parameter-list'))
        copy_files(self._projectOptions.path('top-path'),
                   self._archiveOptions.path('parameter-path'),
                   self._pathsToParameters,
                   createDirectories=True)
        write_json(self._inputData,self._archiveOptions.path('input-files'))
        # output data not yet implemented
        write_json(self._command,self._archiveOptions.path('last-command'))
        #environment not yet implemented



class ExperimentArchiver:

    def __init__(self, archiveName):
        self._archiveName = archiveName
        optionsFile = os.path.join(archiveName,'project.ini')
        self._projectOptions = projectoptions.ProjectOptions(optionsFile)
        self._logger = None

    def find_free_experiment_name(self,rawName):
        today = date.today().strftime('%Y%m%d')   
        number = -1
        experimentPath = ''
        experimentName = ''
        while experimentPath == '' or os.path.isdir(experimentPath) :
            number += 1
            experimentName = "{0}_{1}_{2:02d}".format(today, rawName, number)
            experimentPath = os.path.join(self._archiveName,experimentName)
        return experimentName
    
    def run_and_record(self,command):
        savePath = os.getcwd()
        success = False
        try:
            os.chdir(self._projectOptions.path('build-path'))
            subprocess.check_call(command)
            success = True
        finally:
            os.chdir(savePath)
            write_json({'success':sucess,'command':command},
                       self.projectOptions.path('last-command'))

    def archive(self,rawName):
        experimentName = self.find_free_experiment_name(rawName)
        archiveOptions = archiveoptions.ArchiveOptions(self._archiveName,experimentName)
        state = ExperimentState(self._projectOptions,self._archiveOptions)
        state.read_from_project()
        state.write_to_archive()
        return state

    def restore(self,experimentName):
        archiveOptions = archiveoptions.ArchiveOptions(self._archiveName,experimentName)
        state = ExperimentState(self._projectOptions,self._archiveOptions)
        state.read_from_archive()
        state.restore_to_project()
        return state
    
    def run_and_archive(self,rawName,command):
        self.run_and_record(command)
        state = self.archive(rawName)
        return state
    
    def restore_and_run(self):
        state = self.restore(experimentName)
        command = state.get_command()
        self.run_and_record(command)
        return state
    