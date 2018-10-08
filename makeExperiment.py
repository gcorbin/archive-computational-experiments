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

def readCommandFromFile(filename):
    commandFile = open(filename,'r')
    command = commandFile.readline().strip('\n').split(' ')
    commandFile.close()
    return command

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

        
        print 'verifying hashes of big files...'
        hashesFile = open(experimentPaths['hashed-files'],'r')
        for line in hashesFile:
            splitline = line.strip('\n').split(' ')
            if (len(splitline) != 2):
                raise Exception("Invalid line in hashes file {0}: {1}".format(experimentPaths['hashed-files'],line))
            fileToHash = os.path.join(projectPaths['hashed-files-folder'],splitline[0])
            storedHash = splitline[1]            
            computedHash = utils.computeFileHash(fileToHash)
            if (storedHash != computedHash):
                raise Exception("The stored hash for the file {0} is different from the computed hash for file {1}. {2} != {3}".format(splitline[0],fileToHash,storedHash,computedHash))
            
                
        
        print 'building the executable...'
        savePath = os.getcwd()
        os.chdir(projectPaths['build'])
        #status = check_call((projectConfig['settings']['build-command']).split())
        os.chdir(savePath)

        print 'running the experiment...'
        command = ['./loggedRun.py', projectName]
        command.extend(readCommandFromFile(experimentPaths['last-command']))
        check_call(command)

        print 'successfully made the experiment' , experimentName , 'in project', projectName
        sys.exit(0)
        
    except Exception, Message:
        print 'Failed to load the experiment:'
        print Message
        sys.exit(1)
        
        
    
    
