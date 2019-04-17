import os
import copy
import subprocess
from datetime import date
import logging

import experimentarchiver.os_utils as os_utils
from experimentarchiver.project import Project
from experimentarchiver.experiment import Experiment


logger = logging.getLogger(__name__)


def split_archive_and_experiment_name(path):
    if os.path.isabs(path):
        raise Exception('Only relative paths allowed')
    if os_utils.is_composite(path):
        parts = os_utils.split_all_parts(path)
        archive_name = parts[0]
        experiment_name = os.path.join(*parts[1:])
        return archive_name, experiment_name
    else:
        return '', path


class ExperimentArchiver:

    def __init__(self, archive_name):
        self._archiveName = archive_name
        options_file = os.path.join(archive_name, 'project.ini')
        self._project = Project(options_file)

    def _get_path_to_experiment(self, set_name, experiment_path):
        if set_name != '':
            experiment_path = os.path.join('data', experiment_path)
        return os.path.join(set_name, experiment_path)

    def _get_path_to_set(self, set_name):
        return os.path.join(self._archiveName, set_name)

    def _check_if_set_exists(self, set_name):
        set_path = self._get_path_to_set(set_name)
        if set_name == '':
            return True
        return os.path.isfile(os.path.join(set_path, 'set_description'))

    def _find_free_experiment_path(self, set_name, raw_path):
        head, raw_name = os.path.split(raw_path)

        today = date.today().strftime('%Y%m%d')
        number = -1
        full_experiment_path = ''
        experiment_path = ''
        while full_experiment_path == '' or os.path.isdir(full_experiment_path):
            number += 1
            experiment_name = "{0}_{1}_{2:02d}".format(today, raw_name, number)
            experiment_path = os.path.join(head, experiment_name)
            experiment_path = self._get_path_to_experiment(set_name, experiment_path)
            full_experiment_path = os.path.join(self._archiveName, experiment_path)
        return experiment_path

    def _run_and_record(self, command):
        command_record = {'status': 1, 'command': command}
        try:
            with os_utils.ChangedDirectory(self._project.path('build-path')):
                extra_args = self._project.option('append-arguments')
                augmented_command = copy.copy(command_record['command'])
                augmented_command.extend(extra_args)
                logger.debug('Executing command %s', augmented_command)
                command_record['status'] = subprocess.call(augmented_command)
        finally:
            self._project.record_command(command_record)
        if command_record['status'] != 0:
            logger.warning('Command exited with non-zero status: %s', command_record['status'])
        else:
            logger.info('Successfully executed the command.')
        return command_record

    def run_last_command(self):
        logger.info('Trying recorded run, using last recorded command.')
        command_record = self._project.read_command()
        if len(command_record['command']) > 0:
            if command_record['status'] != 0:
                logger.warning('Running a recorded command with non-zero exit status: %s', command_record['status'])
            return self._run_and_record(command_record['command'])
        else:
            logger.error('Nothing will be run.')
            return command_record

    def run(self, command):
        self._project.build_project()
        logger.info('Trying recorded run, using specified command.')
        return self._run_and_record(command)

    def create_new_set(self, set_name, description=''):
        logger.info('Creating new experiment set %s for project %s', set_name, self._archiveName)
        set_path = self._get_path_to_set(set_name)
        if os.path.isdir(set_path):
            logger.warning('Cannot use an existing folder %s to create a new set', set_path)
            return
        os_utils.make_directory_if_nonexistent(set_path)

        doc_path = os.path.join(set_path, 'doc')
        os_utils.make_directory_if_nonexistent(doc_path)
        os_utils.make_directory_if_nonexistent(os.path.join(set_path, 'data'))

        protocol_template = os.path.join(self._archiveName, 'protocol_template.tex')
        if os.path.isfile(protocol_template):
            os_utils.copy_files(self._archiveName, doc_path, ['protocol_template.tex'])
        else:
            logger.warning('The file %s does not exist. '
                           'Consider writing a template for experiment protocols. ', protocol_template)
        with open(os.path.join(doc_path, 'protocol_macros.tex'), 'w') as f:
            f.write('\\newcommand{\\protocoltitle}{%s}\n' % (set_name, ))
            f.write('\\newcommand{\\protocoldate}{%s}\n' % (date.today().strftime('%d.%m.%Y'), ))
            f.write('\\newcommand{\\protocoldescription}{%s}\n' % (description, ))

        with open(os.path.join(set_path, 'set_description'), 'w') as f:
            f.write(description)

    def archive(self, set_name, raw_name, description=''):
        logger.info('Archiving experiment for project %s', self._archiveName)
        if not self._check_if_set_exists(set_name) :
            raise Exception('There is no valid set with the name {0}'.format(set_name))
        experiment_path = self._find_free_experiment_path(set_name, raw_name)
        logger.info('Experiment name is %s', experiment_path)
        experiment = Experiment(self._archiveName, experiment_path)
        experiment.archive_project(self._project, description)

    def restore(self, experiment_path):
        logger.info('Restoring experiment %s to project %s', experiment_path, self._archiveName)
        experiment = Experiment(self._archiveName, experiment_path)
        self._project.restore_to_project(experiment)