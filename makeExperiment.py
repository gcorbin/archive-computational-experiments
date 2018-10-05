#!/usr/bin/python

import sys 
import os
from subprocess import call
import definePaths as p 
import utils

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
    paths = {}
    paths.update( p.defineProjectPaths(projectName) )
    paths.update( p.defineExperimentPaths(projectName,experimentName) )    
    if (not p.checkIfPathsExist(paths) ) : 
        sys.exit(1)
        
    experimentFiles = p.defineExperimentFiles()
    experimentFilesInExperiment = p.prependPathToFiles(paths['experiment'], experimentFiles)
    if (not p.checkIfFilesExist(experimentFilesInExperiment) ) :
        sys.exit(1)
        
    print 'checking out the git commit ...'
    if (not utils.checkIfGitRepoIsClean(paths['git']) ):
        sys.exit(1)        
    
    commitHash = readCommitHashFromFile(experimentFilesInExperiment['commit'])
    status = checkoutGitCommit(paths['git'],commitHash)
    os.chdir(paths['git'])
    status = call(['git','checkout' , commitHash])
    if (status != 0):
        sys.exit()
    
    print 'copying experiment files...'
    experimentFilesInProject = p.prependPathToFiles(paths['projectConfig'],experimentFiles)
    for key in experimentFilesInExperiment:
        status = call(['cp', experimentFilesInExperiment[key],experimentFilesInProject[key] ])
        if (status != 0):
            print 'could not copy the ', key , 'file' 
            sys.exit()
    
    print 'building the executable'
    os.chdir(paths['projectBuild'])
    status = call(['make', '-B', projectName])
    if (status != 0):
        print 'failed to build the executable' , projectName
        sys.exit()
        
    print 'successfully made the experiment' , experimentName , 'in project', projectName

        
        
    
    