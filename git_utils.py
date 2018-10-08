import os
import sys
from subprocess import  check_call, check_output

def makeGitDiffExcludeList(excludeList):
    modifiedList = []
    for item in excludeList:
        modifiedList.append("\':(exclude){0}\'".format(item))
    return modifiedList


def checkIfGitRepoIsClean(pathToRepo,pathToProject,excludeList):
    savePath = os.getcwd()
    os.chdir(pathToProject)
        
    command = "git diff HEAD --quiet -- " + pathToRepo + " " 
    for item in makeGitDiffExcludeList(excludeList):
        command = command + " " + item
    
    status = os.system(command)
    os.chdir(savePath)
    return (status == 0)
    
    
def getGitCommitHash(pathToRepo):
    savePath = os.getcwd()
    os.chdir(pathToRepo)
    commithash = check_output(['git','rev-parse','master'])
    os.chdir(savePath)
    return commithash


def writeCommitHashToFile(filename,commithash):
    commitFile = open(filename,'w')
    commitFile.write(commithash)
    commitFile.close()
    
    
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