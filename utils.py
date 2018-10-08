import os
from datetime import date
from subprocess import call
from configparser import ConfigParser, ExtendedInterpolation

def makeGitDiffExcludeList(excludeList):
    modifiedList = []
    for item in excludeList:
        modifiedList.append("\':(exclude){0}\'".format(item))
    return modifiedList

def checkIfGitRepoIsClean(pathToRepo,pathToProject,excludeList):
    savePath = os.getcwd()
    os.chdir(pathToProject)
        
    command = "git diff --quiet -- " + pathToRepo + " " 
    for item in makeGitDiffExcludeList(excludeList):
        command = command + " " + item
    
    status = os.system(command)
    os.chdir(savePath)
    return (status == 0)

def getProjectConfig(projectName):
    config = ConfigParser(interpolation = ExtendedInterpolation())
    config.read(os.path.join(projectName,'project.ini'))  
    return config

def makeExperimentNameFromDateNameAndNumber (experimentDate, simulationName, experimentNumber):
    return "{0}_{1}_{2:02d}".format(experimentDate, simulationName, experimentNumber)

def getRelativeExperimentTopPath(projectName, experimentName):
    return os.path.join(projectName,experimentName)

def makeUniqueExperimentName(projectName, simulationName):
    experimentDate=date.today().strftime('%Y%m%d')        
    experimentNumber = 0
    experimentName =  makeExperimentNameFromDateNameAndNumber(experimentDate,simulationName,experimentNumber)
    while (os.path.isdir(getRelativeExperimentTopPath(projectName,experimentName) )):
        experimentNumber  = experimentNumber + 1    
        experimentName    = makeExperimentNameFromDateNameAndNumber(experimentDate,simulationName,experimentNumber)
    return experimentName

def getRelativeExperimentPaths(projectName, experimentName):
    experimentPath = getRelativeExperimentTopPath(projectName,experimentName)
    paths = {'top':experimentPath,\
             'data':os.path.join(experimentPath,'experiment-data/'),\
             'commithash':os.path.join(experimentPath,'commithash'),\
             'last-command':os.path.join(experimentPath,'last-command'),\
             'hashed-files':os.path.join(experimentPath,'hashed-files')}
    return paths

def getListOfExperimentDataFiles(filename):
    filelist = []
    experimentData = open(filename,'r')
    for line in experimentData:
        filelist.append(line.strip())
    experimentData.close()
    return filelist


def computeFileHash(fileToHash):
    return "{0}".format(os.path.getsize(fileToHash))
