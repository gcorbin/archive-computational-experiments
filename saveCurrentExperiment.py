#!/usr/bin/python

import sys 
import os
from datetime import date
from subprocess import call, check_call, check_output
from configparser import ConfigParser, ExtendedInterpolation
import utils
import definePaths as p 
import exceptions


def writeCommitHashToFile(filename,commithash):
    commitFile = open(filename,'w')
    commitFile.write(commithash)
    commitFile.close()
  
def makeAllDirectories(topdir,path):
    dirname = os.path.dirname(path)
    savePath = os.getcwd()
    os.chdir(topdir)
    for level in dirname.split('/'):
        if (not os.path.isdir(level)):
            os.mkdir(level)
        os.chdir(level)
    os.chdir(savePath)
    

def getGitCommitHash(pathToRepo):
    savePath = os.getcwd()
    os.chdir(pathToRepo)
    commithash = check_output(['git','rev-parse','master'])
    os.chdir(savePath)
    return commithash

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
             'commithash':os.path.join(experimentPath,'commithash')}
    return paths

def getListOfExperimentDataFiles(filename):
    filelist = []
    experimentData = open(filename,'r')
    for line in experimentData:
        filelist.append(line.strip())
    experimentData.close()
    return filelist

    
if __name__ == '__main__': 
    try:
        if ( len(sys.argv) < 3) :
            raise Exception('Not enough arguments have been provided. Usage: saveCurrentExperiment <project> <name>')
        projectName = sys.argv[1]
        simulationName = sys.argv[2] 
        print 'saving current experiment in project ', projectName
        projectConfig = getProjectConfig(projectName) 
        projectPaths = projectConfig['paths']
        experimentName = makeUniqueExperimentName(projectName, simulationName)        
        experimentPaths = getRelativeExperimentPaths(projectName, experimentName)        

        experimentFiles = getListOfExperimentDataFiles(projectPaths['experiment-data'])
        
        if (not utils.checkIfGitRepoIsClean(projectPaths['git'],projectPaths['top'], experimentFiles) ):
            raise Exception("There are uncommitted changes in the git repository {0}\nMake sure that the working directory is clean.".format(projectPaths['git'])) 
        
        
        os.mkdir(experimentPaths['top'])        
        try:
            os.mkdir(experimentPaths['data'])            
            
            commithash = getGitCommitHash(projectPaths['top'])
            writeCommitHashToFile(experimentPaths['commithash'],commithash)        
            
            for exfile in experimentFiles:
                fromFile = os.path.join(projectPaths['top'],exfile)
                toFile = os.path.join(experimentPaths['data'],exfile)
                makeAllDirectories(experimentPaths['data'],exfile)
                check_call(['cp', fromFile, toFile ])
            
        except Exception, Message:
            print 'Cleaning up failed attempt at saving'
            check_call(['rm', '-r', experimentPaths['top']])
            raise Exception(Message)
        
        print 'successfully saved the experiment to' , experimentPaths['top']
        sys.exit(0)

    except Exception, Message:
        print 'Failed to save the current Experiment'
        print Message
        sys.exit(1)
        
    
        
    
    
    
    
    