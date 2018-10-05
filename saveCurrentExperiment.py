#!/usr/bin/python

import sys 
import os
from datetime import date
from subprocess import call, check_output
from configparser import ConfigParser, ExtendedInterpolation
import utils
import definePaths as p 

def makeExperimentName (experimentDate, simulationName, experimentNumber):
    return "{0}_{1}_{2:02d}".format(experimentDate, simulationName, experimentNumber)


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

if __name__ == '__main__': 
    if ( len(sys.argv) < 3) :
        print 'Usage : ', sys.argv[0], ' <project> <name>'
        sys.exit(1)
    projectName = sys.argv[1]
    simulationName = sys.argv[2] 
    print 'saving current experiment in project ', projectName
    config = ConfigParser(interpolation = ExtendedInterpolation())
    config.read(os.path.join(projectName,'project.ini'))                    
    paths = config['paths']        
    
    print 'extracting experiment name...'        
    experimentDate=date.today().strftime('%Y%m%d')
    
    experimentNumber = 0
    experimentName =  makeExperimentName(experimentDate,simulationName,experimentNumber)
    while (os.path.isdir(os.path.join(projectName,experimentName) )):
        experimentNumber  = experimentNumber + 1    
        experimentName    = makeExperimentName(experimentDate,simulationName,experimentNumber)
     
    experimentPath = os.path.join(projectName,experimentName)  
    os.mkdir(experimentPath)
    os.mkdir(os.path.join(experimentPath,'experiment-data'))
    
    print 'extracting git commit hash...'
    if (not utils.checkIfGitRepoIsClean(paths['top']) ):
        sys.exit(1)   
    commithash = getGitCommitHash(paths['top'])
    writeCommitHashToFile(os.path.join(experimentPath,'commithash'),commithash)
    
    
    
    experimentData = open(os.path.join(paths['top'],'experiment-data'),'r')
    for line in experimentData:
        relativePath = line.strip()
        fromFile = os.path.join(paths['top'],relativePath)
        toFile = os.path.join(experimentPath,'experiment-data',relativePath)
        makeAllDirectories(os.path.join(experimentPath,'experiment-data'),relativePath)
        status = call(['cp', fromFile, toFile ])
        if (status != 0):
            print 'could not copy the file', fromFile 
            sys.exit()
    experimentData.close()
    
            
    print 'successfully saved the experiment to' , experimentPath
    
    
    
    
    