import os
import sys
from subprocess import  call, check_call, check_output

def makeGitDiffExcludeList(excludeList):
    modifiedList = []
    for item in excludeList:
        modifiedList.append("':(exclude){0}'".format(item))
    return modifiedList


def checkIfGitRepoIsClean(pathToRepo,pathToProject,excludeList):
    command = ['git', '-C', pathToProject, 'diff', 'HEAD','--quiet', '--', pathToRepo]
    for item in makeGitDiffExcludeList(excludeList):
        command.append(item)
    commandstr = ''
    for arg in command:
        commandstr = commandstr + ' ' + arg
    status = os.system(commandstr) # somehow the subprocess.call method does not work here
    return (status == 0)


def getGitCommitHash(pathToRepo):
    commithash = check_output(['git','-C',pathToRepo,'rev-parse','master'])
    # In Python 3 the check_output function returns a byte-array,
    # that has to be converted to a string
    commithash = commithash.decode('utf-8')
    commithash = commithash.strip('\n').strip()
    return commithash


def checkoutGitCommit(pathToRepo,commitHash):
    check_call(['git','-C',pathToRepo,'checkout' , commitHash])