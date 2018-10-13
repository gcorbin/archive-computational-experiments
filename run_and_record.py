#!/usr/bin/python

import sys
from experimentarchiver.defaultlogger import set_default_logging_behavior
from experimentarchiver.archiver import ExperimentArchiver


if __name__ == '__main__': 
    set_default_logging_behavior(logfile='run_and_record')
    if ( len(sys.argv) < 3) :
        raise Exception('Not enough arguments have been provided. Usage: run_and_record <project> <command with args>')
    projectName = sys.argv[1]
    command = sys.argv[2:]
    archiver = ExperimentArchiver(projectName)
    archiver.run_and_record(command)
    sys.exit(0)

