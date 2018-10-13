#!/usr/bin/python

import sys
from experimentarchiver.archiver import ExperimentArchiver
from experimentarchiver.defaultlogger import set_default_logging_behavior


if __name__ == '__main__':

    set_default_logging_behavior(logfile='archive')
    if ( len(sys.argv) < 3) :
            raise Exception('Not enough arguments have been provided. Usage: archive <project> <simulation name>')
    projectName = sys.argv[1]
    simulationName = sys.argv[2]
    archiver = ExperimentArchiver(projectName)
    archiver.archive(simulationName)
    sys.exit(0)
