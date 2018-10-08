import os
from datetime import date
from subprocess import call
from configparser import ConfigParser, ExtendedInterpolation
import hashlib


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

def getRelativeExperimentPaths(experimentTop):
    paths = {'top':experimentTop,\
             'data':os.path.join(experimentTop,'experiment-data/'),\
             'commithash':os.path.join(experimentTop,'commithash'),\
             'last-command':os.path.join(experimentTop,'last-command'),\
             'hashed-files':os.path.join(experimentTop,'hashed-files')}
    return paths

def getListOfExperimentDataFiles(filename):
    filelist = []
    experimentData = open(filename,'r')
    for line in experimentData:
        filelist.append(line.strip())
    experimentData.close()
    return filelist


def computeFileHash(fileName, hashAlgorithm):
    fileHash = hashlib.new(hashAlgorithm)
    
    bufferSize = 64 * pow(2,10) 
    fileToHash = open(fileName,'r')
    while True:
        chunk = fileToHash.read(bufferSize)
        if (not chunk):
            break
        fileHash.update(chunk)
    fileToHash.close()
        
    return "{0}".format(fileHash.hexdigest())
