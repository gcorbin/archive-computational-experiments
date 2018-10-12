from experimentarchiver.archiver import ExperimentArchiver, split_archive_and_experiment_name

projectName = 'kershaw-ap'
command = 'mpirun -n 4 ./kershaw-ap'.split(' ')
archiver = ExperimentArchiver(projectName)
archiver.run_and_record(command)
state = archiver.archive('Fibreend')
experimentPath = state._archiveOptions.option('experiment-path')
archiveName, experimentName = split_archive_and_experiment_name(experimentPath)
archiver.restore_and_run(experimentName)