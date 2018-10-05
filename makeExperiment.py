#!/usr/bin/python

import sys 
import os
from subprocess import call
import definePaths as p 
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
    status = call(['git','checkout' , commitHash])
    if (status != 0):
        print 'could not checkout git commit with hash', commitHash
    os.chdir(savePath)
    return status

if __name__ == '__main__': 
    if ( len(sys.argv) < 3) :
        print 'Usage :', sys.argv[0], ' <project> <experiment>'
        sys.exit(1)
    projectName = sys.argv[1]
    experimentName = sys.argv[2]
    print 'making experiment', experimentName , ' in project ', projectName, '.'
    print 'checking paths and files...'
    config = ConfigParser(interpolation = ExtendedInterpolation())
    config.read(os.path.join(projectName,'project.ini'))
                   
    experimentPath = os.path.join(projectName,experimentName)    
    paths = config['paths']        
        
    print 'checking out the git commit ...'
    if (not utils.checkIfGitRepoIsClean(paths['top']) ):
        sys.exit(1)   
    
    commitHash = readCommitHashFromFile( os.path.join(experimentPath,'commithash') )
    status = checkoutGitCommit(paths['top'],commitHash)
    
    print 'copying experiment files...'
    experimentData = open(os.path.join(paths['top'],'experiment-data'),'r')
    for line in experimentData:
        relativePath = line.strip()
        fromFile = os.path.join(experimentPath,'experiment-data',relativePath)
        toFile  = os.path.join(paths['top'],relativePath)
        status = call(['cp', fromFile, toFile ])
        if (status != 0):
            print 'could not copy the file', fromFile 
            sys.exit()
    experimentData.close()
    
    print 'building the executable'
    os.chdir(paths['build'])
    status = call((config['settings']['build-command']).split())
    if (status != 0):
        print 'failed to build the executable' , projectName
        sys.exit()
        
    print 'successfully made the experiment' , experimentName , 'in project', projectName
        
        
    
    