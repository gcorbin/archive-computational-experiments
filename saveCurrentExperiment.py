#!/usr/bin/python

import sys 
import os
from subprocess import call, check_call, check_output
import utils
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

    
if __name__ == '__main__': 
    try:
        if ( len(sys.argv) < 3) :
            raise Exception('Not enough arguments have been provided. Usage: saveCurrentExperiment <project> <name>')
        projectName = sys.argv[1]
        simulationName = sys.argv[2] 
        print 'saving current experiment in project ', projectName
        projectConfig = utils.getProjectConfig(projectName) 
        projectPaths = projectConfig['paths']
        experimentName = utils.makeUniqueExperimentName(projectName, simulationName)        
        experimentPaths = utils.getRelativeExperimentPaths(projectName, experimentName) 
        experimentFiles = utils.getListOfExperimentDataFiles(projectPaths['experiment-data'])
        
        if (not utils.checkIfGitRepoIsClean(projectPaths['git'],projectPaths['top'], experimentFiles) ):
            raise Exception("There are uncommitted changes in the git repository {0}\nMake sure that the working directory is clean.".format(projectPaths['git'])) 
        
        
        os.mkdir(experimentPaths['top'])        
        try:
            os.mkdir(experimentPaths['data'])            
            
            print 'saving git commit hash...'
            commithash = getGitCommitHash(projectPaths['top'])
            writeCommitHashToFile(experimentPaths['commithash'],commithash)        
            
            print 'saving experiment files...'
            for exfile in experimentFiles:
                fromFile = os.path.join(projectPaths['top'],exfile)
                toFile = os.path.join(experimentPaths['data'],exfile)
                makeAllDirectories(experimentPaths['data'],exfile)
                check_call(['cp', fromFile, toFile ])
            
        except Exception, Message:
            print 'Cleaning up failed attempt at saving...'
            check_call(['rm', '-r', experimentPaths['top']])
            raise Exception(Message)
        
        print 'successfully saved the experiment to' , experimentPaths['top']
        sys.exit(0)

    except Exception, Message:
        print 'Failed to save the current experiment:'
        print Message
        sys.exit(1)
        
    
        
    
    
    
    
    