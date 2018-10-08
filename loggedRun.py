#!/usr/bin/python

import sys 
import os
from subprocess import check_call
import project_utils, git_utils

def runCommandInFolder(command,folder):
    savePath = os.getcwd()
    os.chdir(folder)
    check_call(command)
    os.chdir(savePath)


if __name__ == '__main__': 
    try: 
        if ( len(sys.argv) < 3) :
            raise Exception('Not enough arguments have been provided. Usage: runAndSaveArguments <project> <command with args>')
        projectName = sys.argv[1]
        projectConfig = project_utils.getProjectConfig(projectName) 
        projectPaths = projectConfig['paths']  
        numargs = len(sys.argv)
        command = sys.argv[2:numargs]

        commandfile = open(projectPaths['last-command'],'w')
        commandfile.close()

        runCommandInFolder(command,projectPaths['build'])
        
        commandfile = open(projectPaths['last-command'],'w')
        
        for pair in enumerate(command):
            commandfile.write(pair[1])
            if pair[0] < len(command) - 1:
                commandfile.write(' ')
        commandfile.close()
    
        print 'successfully run command in project', projectName
        sys.exit(0)

    except Exception, Message:
        print 'Failed to run the experiment:'
        print Message
        sys.exit(1)
