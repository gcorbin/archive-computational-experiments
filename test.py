import Beholding.os_utils as os_utils
from Beholding.archivist import Archivist

projectName = 'Testproject'
command = './do-stuff order. reverse in is sentence This'.split(' ')
archiver = Archivist(projectName)
archiver.run_and_record(command)
state = archiver.archive('stuff')
experimentPath = state._archiveOptions.path('experiment-path')
archiveName, experimentName = os_utils.split_path_after_first_component(experimentPath)
archiver.remember(experimentName)
archiver.replay()