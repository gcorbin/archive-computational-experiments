import os
from subprocess import call

def makeGitDiffExcludeList(excludeList):
    modifiedList = []
    for item in excludeList:
        modifiedList.append("\':(exclude){0}\'".format(item))
    return modifiedList

def checkIfGitRepoIsClean(pathToRepo,pathToProject,excludeList):
    savePath = os.getcwd()
    os.chdir(pathToProject)
        
    command = "git diff --quiet -- " + pathToRepo + " " 
    for item in makeGitDiffExcludeList(excludeList):
        command = command + " " + item
    
    status = os.system(command)
    os.chdir(savePath)
    return (status == 0)
