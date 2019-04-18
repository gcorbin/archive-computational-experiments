import os
import logging
import shutil

from Beholding import Version
from Beholding import version as current_version
import Beholding.statement as statement
import os_utils


logger = logging.getLogger(__name__)


class Casefile:
    
    def __init__(self, archive_path, casefile_name):
        casefile_path = os.path.join(archive_path, casefile_name)
        self._paths = {'archive-path': archive_path,
                       'experiment-path': casefile_path,
                       'parameter-path': os.path.join(casefile_path, 'parameters/'),
                       'output-path': os.path.join(casefile_path, 'outputs/'),
                       'parameter-list': os.path.join(casefile_path, 'parameters/parameter-list'),
                       'commit-hash': os.path.join(casefile_path, 'commit-hash'),
                       'last-command': os.path.join(casefile_path, 'last-command'),
                       'input-files': os.path.join(casefile_path, 'input-files'),
                       'description': os.path.join(casefile_path, 'description'),
                       'version': os.path.join(casefile_path, 'version')}

    def path(self, key):
        return self._paths[key]

    def _check_version(self):
        logger.debug('Reading version number from file %s', self.path('version'))
        if os.path.isfile(self.path('version')):
            try:
                stored_version = Version(*statement.read_json(self.path('version')))
            except (ValueError, TypeError):
                logger.warning('The version file is corrupted. Cannot parse the version number.')
                return
            if current_version == stored_version:
                logger.info('The current program version %s matches the version used to record the statement.',
                            str(current_version))
            else:
                if current_version > stored_version:
                    comp = 'NEWER'
                else:
                    comp = 'OLDER'
                logger.warning('The current program version %s is %s'
                               ' than the version %s used to record the statement.',
                               str(current_version), comp, str(stored_version))
        else:
            logger.warning('There is no version file for this casefile. '
                           'This statement seems to be very old.')

    def read_from_archive(self):
        state = statement.Statement()
        logger.info('Reading from archive.')
        self._check_version()
        logger.debug('Case file directory is %s', self.path('experiment-path'))
        state.commitHash = statement.read_json(self.path('commit-hash'))
        state.pathsToParameters = statement.read_json(self.path('parameter-list'))
        state.inputData = statement.read_json(self.path('input-files'))
        state.command = statement.read_json(self.path('last-command'))
        state.environment = None  # not yet implemented
        with open(self.path('description'), 'r') as f:
            state.description = f.readline().strip('\n')
        logger.info('Statement description: %s ...', state.description)
        state.pathsToOutputData = []  # nothing to do
        return state

    def write_to_archive(self, project, state):
        logger.info('Writing statement to archive.')
        os_utils.make_all_directories(self.path('experiment-path'))
        logger.debug('Case file directory is %s', self.path('experiment-path'))
        if not current_version.is_release():
            logger.warning('This version of the Archivist is not a release and potentially unstable. '
                           'Consider using a stable version instead.')
        statement.write_json(current_version.get_version_tuple(), self.path('version'))
        statement.write_json(state.commitHash, self.path('commit-hash'))
        os_utils.make_directory_if_nonexistent(self.path('parameter-path'))
        statement.write_json(state.pathsToParameters, self.path('parameter-list'))
        os_utils.copy_files(project.path('top-path'),
                            self.path('parameter-path'),
                            state.pathsToParameters,
                            create_directories=True)
        statement.write_json(state.inputData, self.path('input-files'))
        statement.write_json(state.command, self.path('last-command'))
        # environment not yet implemented
        with open(self.path('description'), 'w') as f:
            f.write(state.description)
        if project.option('do-record-outputs'):
            logger.info('Copying outputs to archive.')
            os_utils.make_directory_if_nonexistent(self.path('output-path'))
            os_utils.copy_changed_files(project.path('output-data-path'), self.path('output-path'), state.pathsToOutputData)

    def archive_project(self, project, description=None):
        state = project.read_from_project()
        if description is not None:
            state.description = description
        if state.command['status'] != 0:
            raise Exception('Archiving failed runs is not allowed.')
        try:
            self.write_to_archive(project, state)
        except Exception:
            logger.warning('Cleaning up failed archiving attempt.')
            logger.debug('Removing directory %s', self.path('experiment-path'))
            shutil.rmtree(self.path('experiment-path'), ignore_errors=True)
            raise
