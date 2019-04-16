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
    parts = os_utils.split_all_parts(path)
    archive_name = parts[0]
    experiment_name = os.path.join(*parts[1:])
    return archive_name, experiment_name


class ExperimentArchiver:

    def __init__(self, archive_name):
        self._archiveName = archive_name
        options_file = os.path.join(archive_name, 'project.ini')
        self._project = Project(options_file)

    def find_free_experiment_path(self, raw_path):
        parts = os_utils.split_all_parts(raw_path)
        raw_name = parts.pop()
        path_to_experiment = os.path.join(".", *parts)

        today = date.today().strftime('%Y%m%d')
        number = -1
        full_experiment_path = ''
        experiment_path = ''
        while full_experiment_path == '' or os.path.isdir(full_experiment_path):
            number += 1
            experiment_name = "{0}_{1}_{2:02d}".format(today, raw_name, number)
            experiment_path = os.path.join(path_to_experiment, experiment_name)
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
        logger.info('Trying recorded run, using specified command.')
        return self._run_and_record(command)

    def archive(self, raw_path, description=''):
        logger.info('Archiving experiment for project %s', self._archiveName)
        experiment_path = self.find_free_experiment_path(raw_path)
        logger.info('Experiment name is %s', experiment_path)
        experiment = Experiment(self._archiveName, experiment_path)
        experiment.archive_project(self._project, description)

    def restore(self, experiment_path):
        logger.info('Restoring experiment %s to project %s', experiment_path, self._archiveName)
        experiment = Experiment(self._archiveName, experiment_path)
        self._project.restore_to_project(experiment)
    
    def run_and_archive(self, raw_name, command):
        self.run(command)
        self.archive(raw_name)
    
    def restore_and_run(self, experiment_name):
        self.restore(experiment_name)
        self.run_last_command()
