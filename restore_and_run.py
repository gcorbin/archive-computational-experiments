#!/usr/bin/python

import sys
from experimentarchiver.archiver import ExperimentArchiver, split_archive_and_experiment_name


if __name__ == '__main__': 

    if ( len(sys.argv) < 2) :
            raise Exception('Not enough arguments have been provided. Usage: restore <experiment>')
    experimentPath = sys.argv[1]
    archiveName , experimentName = split_archive_and_experiment_name(experimentPath)

    print 'Making experiment', experimentName , 'in project', archiveName, '...'
    archiver = ExperimentArchiver(archiveName)
    archiver.restore_and_run(experimentName)
    sys.exit(0)