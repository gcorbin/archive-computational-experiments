#!/usr/bin/python

import sys
from experimentarchiver.archiver import ExperimentArchiver


if __name__ == '__main__': 

    if ( len(sys.argv) < 3) :
            raise Exception('Not enough arguments have been provided. Usage: archive <project> <simulation name>')
    projectName = sys.argv[1]
    simulationName = sys.argv[2] 
    print 'Saving current experiment in project {0} ...'.format(projectName)
    archiver = ExperimentArchiver(projectName)
    archiver.archive(simulationName)
    sys.exit(0)
