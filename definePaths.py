import os

def defineProjectPaths(projectName):
    gitPath = '/home/greg/Code/DUNE/dune-kershaw/'
    projectTopPath = gitPath + projectName + '/'
    projectConfigPath = projectTopPath + 'dune/' + projectName + '/config/'
    projectBuildPath = projectTopPath + 'build-cmake/src/'
    paths = {'git':gitPath,\
             'projectTop':projectTopPath,\
             'projectConfig':projectConfigPath,\
             'projectBuild':projectBuildPath}
    return paths


def defineExperimentPaths(projectName,experimentName):
    experimentTopPath=os.getcwd()
    experimentPath=experimentTopPath + '/' + projectName + '/' + experimentName + '/'
    paths = {'experimentTop':experimentTopPath,\
             'experiment':experimentPath}
    return paths


def defineExperimentFiles():  
    files = {'commit': 'commitnumber',\
             'traits': 'traits.hh',\
             'parameters': 'parameters.ini'}
    return files

def prependPathToFiles(path, files):
    filesWithPath = {}
    for key, value in files.items():
        filesWithPath[key] = os.path.join(path,value)
    return filesWithPath
    

def checkIfPathsExist(paths):
    for path in paths.values(): 
        if (not os.path.isdir(path)):
            print 'The directory ', path, 'does not exist.'
            return False
    return True

def checkIfFilesExist(files):
    for file in files.values(): 
        if (not os.path.isfile(file)):
            print 'The file ', file, 'does not exist.'
            return False
    return True


