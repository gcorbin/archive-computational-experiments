from Beholding.archivist import ExperimentArchiver, split_archive_and_experiment_name

projectName = 'Testproject'
command = './do-stuff order. reverse in is sentence This'.split(' ')
archiver = ExperimentArchiver(projectName)
archiver.run_and_record(command)
state = archiver.archive('stuff')
experimentPath = state._archiveOptions.path('experiment-path')
archiveName, experimentName = split_archive_and_experiment_name(experimentPath)
archiver.restore(experimentName)
archiver.run_last_command()