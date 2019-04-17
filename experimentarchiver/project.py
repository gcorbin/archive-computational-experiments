import configparser
import logging
import imp
import os
import hashlib
import subprocess

import experimentarchiver.state as experimentstate
import git_utils
import os_utils

logger = logging.getLogger(__name__)


def read_parameter_list(filename):
    logger.info('Reading list of parameter files')
    logger.debug('... from file %s', filename)
    with open(filename, 'r') as f:
        line_list = [line.strip() for line in f]
    return line_list


def get_paths_to_input_data(path_to_script):
    imported_module = imp.load_source('tmp_script_module', path_to_script)
    execute_path = os.path.dirname(path_to_script)
    with os_utils.ChangedDirectory(execute_path):
        logger.info('Retrieving list of input files.')
        logger.debug('... using script file %s', path_to_script)
        path_list = imported_module.get_input_data_files()
    return path_list


def compute_file_hash(filename, hash_algorithm):
    logger.debug('Computing hash for file %s', filename)
    file_hash = hashlib.new(hash_algorithm)

    buffer_size = 64 * pow(2, 10)  # 64 kilobytes
    with open(filename, 'rb') as file_to_hash:
        while True:
            chunk = file_to_hash.read(buffer_size)
            if not chunk:
                break
            file_hash.update(chunk)

    return "{0}".format(file_hash.hexdigest())


class Project:

    def __init__(self, options_file_name):
        logger.debug('Reading options from file %s', options_file_name)
        if not os.path.isfile(options_file_name):
            logger.critical('The file %s does not exist', options_file_name)
            raise OSError('The file {0} does not exist'.format(options_file_name))

        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(options_file_name)
        
        self._options = {}
        self._options['do-git-checkout'] = config.getboolean('options', 'do-git-checkout', fallback=False)
        self._options['do-build'] = config.getboolean('options', 'do-build', fallback=False)
        if self._options['do-build']:
            self._options['build-command'] = config.get('options', 'build-command')
        else:
            self._options['build-command'] = ''
        self._options['do-record-outputs'] = config.getboolean('options', 'do-record-outputs', fallback=False)
        self._options['hash-algorithm'] = config.get('options', 'hash-algorithm', fallback='sha256')
        extra_args = config.get('options', 'append-arguments', fallback='')
        extra_args = extra_args.strip()
        if extra_args == '':
            self._options['append-arguments'] = []
        else:
            self._options['append-arguments'] = extra_args.split(' ')
        
        self._paths = {}
        for key in ['git-path', 'top-path', 'build-path', 'input-data-path',
                    'parameter-list', 'last-command',
                    'output-data-path', 'get-input-files']:
            self._paths[key] = config.get('paths', key)
        if self.option('do-record-outputs'):
            self._paths['output-changes'] = config.get('paths', 'output-changes')

        self._output_snapshot = None
        self._output_changes = []

    def path(self, key):
        return self._paths[key]

    def option(self, key):
        return self._options[key]

    def read_command(self):
        logger.info('Reading status of last command')
        logger.debug('... from file %s', self.path('last-command'))
        record_file = self.path('last-command')
        try:
            command_record = experimentstate.read_json(record_file)
        except IOError:
            logger.error('Could not find a record of the last command in %s', record_file)
            return {'status': 1, 'command': []}
        return command_record

    def record_command(self, command_record):
        logger.info('Recording status of last command')
        logger.debug('... to file %s', self.path('last-command'))
        experimentstate.write_json(command_record, self.path('last-command'))

    def take_output_snapshot(self):
        if self.option('do-record-outputs'):
            snapshot = os_utils.create_snapshot(self.path('output-data-path'))
            if self._output_snapshot is not None:
                self._output_changes = os_utils.compute_changed_files(self._output_snapshot, snapshot)
            self._output_snapshot = snapshot

    def record_output_changes(self):
        if self.option('do-record-outputs'):
            logger.info('Recording changes in output folder')
            logger.debug('Output folder is %s', self.path('output-data-path'))
            experimentstate.write_json(self._output_changes, self.path('output-changes'))

    def read_output_changes(self):
        if self.option('do-record-outputs'):
            logger.info('Reading changed outputs')
            logger.debug('... from file %s', self.path('output-changes'))
            changes_file = self.path('output-changes')
            try:
                output_changes = experimentstate.read_json(changes_file)
            except IOError:
                logger.error('Could not find a record of the output changes in %s', changes_file)
                return []
            return output_changes

    def _hash_input_data(self):
        logger.info('Hashing input data.')
        relative_paths_to_input_data = get_paths_to_input_data(self.path('get-input-files'))
        hash_algorithm = self.option('hash-algorithm')
        data = []
        for relpath in relative_paths_to_input_data:
            abspath = os.path.join(self.path('input-data-path'), relpath)
            file_hash = compute_file_hash(abspath, hash_algorithm)
            hash_tuple = (relpath, hash_algorithm, file_hash)
            data.append(hash_tuple)
        return data

    def _verify_hashes(self, hash_list):
        logger.info('Verifying hashes.')
        for (relpath, hash_algorithm, stored_hash) in hash_list:
            abspath = os.path.join(self.path('input-data-path'), relpath)
            computed_hash = compute_file_hash(abspath, hash_algorithm)
            if stored_hash != computed_hash:
                raise Exception("The stored and computed {0} hashes for the file {1} differ: {2} != {3}"
                                .format(hash_algorithm, abspath, stored_hash, computed_hash))

    def build_project(self):
        if self.option('do-build'):
            logger.info('Building project.')
            build_command = self.option('build-command').strip().split()
            with os_utils.ChangedDirectory(self.path('build-path')):
                logger.debug('Executing build command %s', str(build_command))
                subprocess.check_call(build_command)

    def read_from_project(self):
        state = experimentstate.ExperimentState()
        state.commitHash = git_utils.get_git_commit_hash(self.path('git-path'))
        state.pathsToParameters = read_parameter_list(self.path('parameter-list'))
        repo_is_clean = git_utils.is_git_repo_clean(self.path('git-path'),
                                                    self.path('top-path'),
                                                    state.pathsToParameters)
        if not repo_is_clean:
            raise Exception('The git repository contains unstaged or uncommitted changes')
        state.inputData = self._hash_input_data()
        state.pathsToOutputData = self.read_output_changes()
        state.command = self.read_command()
        state.environment = None  # not yet implemented
        return state

    def restore_to_project(self, experiment):
        state = experiment.read_from_archive()
        paths_to_parameters = read_parameter_list(self.path('parameter-list'))
        repo_is_clean = git_utils.is_git_repo_clean(self.path('git-path'),
                                                    self.path('top-path'),
                                                    paths_to_parameters)
        if not repo_is_clean:
            raise Exception('The git repository contains unstaged or uncommitted changes')
        git_utils.checkout_git_commit(self.path('git-path'), state.commitHash)
        os_utils.copy_files(experiment.path('parameter-path'),
                            self.path('top-path'),
                            state.pathsToParameters,
                            create_directories=False)
        self._verify_hashes(state.inputData)
        # output data will not be restored
        self.record_command(state.command)
        # environment not implemented
        self.build_project()
