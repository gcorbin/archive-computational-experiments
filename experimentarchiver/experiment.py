import os
import logging
import shutil

import experimentarchiver.state as experimentstate
import os_utils

logger = logging.getLogger(__name__)


class Experiment:
    
    def __init__(self, archive_path, experiment_name):
        experiment_path = os.path.join(archive_path, experiment_name)
        self._paths = {'archive-path': archive_path,
                       'experiment-path': experiment_path,
                       'parameter-path': os.path.join(experiment_path, 'parameters/'),
                       'parameter-list': os.path.join(experiment_path, 'parameters/parameter-list'),
                       'commit-hash': os.path.join(experiment_path, 'commit-hash'),
                       'last-command': os.path.join(experiment_path, 'last-command'),
                       'input-files': os.path.join(experiment_path, 'input-files'),
                       'description': os.path.join(experiment_path, 'description')}

    def path(self, key):
        return self._paths[key]

    def read_from_archive(self):
        state = experimentstate.ExperimentState()
        logger.info('Reading from archive')
        logger.debug('Experiment directory is %s', self.path('experiment-path'))
        state.commitHash = experimentstate.read_json(self.path('commit-hash'))
        state.pathsToParameters = experimentstate.read_json(self.path('parameter-list'))
        state.inputData = experimentstate.read_json(self.path('input-files'))
        state.pathsToOutputData = []  # not yet implemented
        state.command = experimentstate.read_json(self.path('last-command'))
        state.environment = None  # not yet implemented
        with open(self.path('description'), 'r') as f:
            state.description = f.readline().strip('\n')
        logger.info('Experiment description: %s ...', state.description)
        return state

    def write_to_archive(self, project, state):
        logger.info('Writing to archive')
        os_utils.make_directory_if_nonexistent(self.path('archive-path'))
        os_utils.make_directory_if_nonexistent(self.path('experiment-path'))
        logger.debug('Experiment directory is %s', self.path('experiment-path'))
        experimentstate.write_json(state.commitHash, self.path('commit-hash'))
        os_utils.make_directory_if_nonexistent(self.path('parameter-path'))
        experimentstate.write_json(state.pathsToParameters, self.path('parameter-list'))
        os_utils.copy_files(project.path('top-path'),
                            self.path('parameter-path'),
                            state.pathsToParameters,
                            create_directories=True)
        experimentstate.write_json(state.inputData, self.path('input-files'))
        # output data not yet implemented
        experimentstate.write_json(state.command, self.path('last-command'))
        # environment not yet implemented
        with open(self.path('description'), 'w') as f:
            f.write(state.description)

    def archive_project(self, project, description=None):
        state = project.read_from_project()
        if description is not None:
            state.description = description
        if state.command['status'] != 0:
            logger.error('Archiving failed runs is not allowed')
            raise Exception('Archiving failed runs is not allowed')
        try:
            self.write_to_archive(project, state)
        except Exception:
            logger.warning('Cleaning up failed archiving attempt.')
            logger.debug('Removing directory %s', self.path('experiment-path'))
            shutil.rmtree(self.path('experiment-path'), ignore_errors=True)
            raise
