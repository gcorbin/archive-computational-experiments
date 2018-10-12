#!/usr/bin/python

import sys
from experimentarchiver.archiver import ExperimentArchiver


if __name__ == '__main__': 

    if ( len(sys.argv) < 3) :
        raise Exception('Not enough arguments have been provided. Usage: run_and_record <project> <command with args>')
    projectName = sys.argv[1]
    command = sys.argv[2:]
    print 'Running command {0} in project {1} ...'.format(str(command),projectName)
    archiver = ExperimentArchiver(projectName)
    archiver.run_and_record(command)
    sys.exit(0)

