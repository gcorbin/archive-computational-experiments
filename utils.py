import os
from subprocess import call

def checkIfGitRepoIsClean(pathToRepo):
    savePath = os.getcwd()
    os.chdir(pathToRepo)
    status = call(['git','diff','--quiet'])
    os.chdir(savePath)
    if (status != 0) :
        print 'There are uncommitted changes in the git repository', pathToRepo
        print 'Make sure that your working directory is clean'
        return False
    return True