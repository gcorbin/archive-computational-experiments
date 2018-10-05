#!/usr/bin/python

import sys 
import os
from subprocess import check_call
import utils
from configparser import ConfigParser, ExtendedInterpolation

def readCommitHashFromFile(filename):
    commitFile = open(filename,'r')
    commitHash = commitFile.readline().strip('\n')
    commitFile.close()
    return commitHash

def checkoutGitCommit(pathToRepo,commitHash):
    savePath = os.getcwd()
    os.chdir(pathToRepo)
    check_call(['git','checkout' , commitHash])
    os.chdir(savePath)

if __name__ == '__main__': 
    try: 
        if ( len(sys.argv) < 3) :
            raise Exception('Not enough arguments have been provided. Usage: makeExperiment <project> <experiment>')
        projectName = sys.argv[1]
        experimentName = sys.argv[2]        
        print 'making experiment', experimentName , ' in project ', projectName, '.'    
        projectConfig = utils.getProjectConfig(projectName) 
        projectPaths = projectConfig['paths']  
        experimentPaths = utils.getRelativeExperimentPaths(projectName, experimentName)        
        experimentFiles = utils.getListOfExperimentDataFiles(projectPaths['experiment-data'])
        
        if (not utils.checkIfGitRepoIsClean(projectPaths['git'],projectPaths['top'], experimentFiles) ):
            raise Exception("There are uncommitted changes in the git repository {0}\nMake sure that the working directory is clean.".format(projectPaths['git'])) 
            
        print 'checking out git commit...'
        commitHash = readCommitHashFromFile( experimentPaths['commithash'] )
        checkoutGitCommit(projectPaths['git'],commitHash)

        print 'loading experiment files...'
        for exfile in experimentFiles:
            fromFile = os.path.join(experimentPaths['data'],exfile)
            toFile  = os.path.join(projectPaths['top'],exfile)
            check_call(['cp', fromFile, toFile ])
        
        print 'building the executable...'
        os.chdir(projectPaths['build'])
        status = check_call((projectConfig['settings']['build-command']).split())

        print 'successfully made the experiment' , experimentName , 'in project', projectName
        sys.exit(0)
        
    except Exception, Message:
        print 'Failed to load the experiment:'
        print Message
        sys.exit(1)
        
        
    
    