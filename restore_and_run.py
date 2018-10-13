#!/usr/bin/python

import sys
from experimentarchiver.archiver import ExperimentArchiver, split_archive_and_experiment_name
from experimentarchiver.defaultlogger import set_default_logging_behavior


if __name__ == '__main__':

    set_default_logging_behavior(logfile='restore_and_run')
    if ( len(sys.argv) < 2) :
            raise Exception('Not enough arguments have been provided. Usage: restore <experiment>')
    experimentPath = sys.argv[1]
    archiveName , experimentName = split_archive_and_experiment_name(experimentPath)
    archiver = ExperimentArchiver(archiveName)
    archiver.restore_and_run(experimentName)
    sys.exit(0)