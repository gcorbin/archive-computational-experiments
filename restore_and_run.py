#!/usr/bin/python

import sys 
import os
import experimentarchiver


if __name__ == '__main__': 

    if ( len(sys.argv) < 2) :
            raise Exception('Not enough arguments have been provided. Usage: restore <experiment>')
    experimentPath = sys.argv[1]
    archiveName , experimentName = experimentarchiver.split_archive_and_experiment_name(experimentPath)

    print 'Making experiment', experimentName , 'in project', archiveName, '...'
    archiver = experimentarchiver.ExperimentArchiver(archiveName)
    archiver.restore_and_run(experimentName)
    sys.exit(0)