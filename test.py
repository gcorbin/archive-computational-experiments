import sys 
import os
import experimentarchiver

projectName = 'kershaw-ap'
command = 'mpirun -n 4 ./kershaw-ap'.split(' ')
archiver = experimentarchiver.ExperimentArchiver(projectName)
archiver.run_and_record(command)
state = archiver.archive('Fibreend')
experimentPath = state._archiveOptions.option('experiment-path')
archiveName, experimentName = experimentarchiver.split_archive_and_experiment_name(experimentPath)
archiver.restore_and_run(experimentName)