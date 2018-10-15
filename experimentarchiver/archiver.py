import os
import copy
import subprocess
from datetime import date
import logging

import experimentarchiver.os_utils as os_utils
from experimentarchiver.project import Project
from experimentarchiver.experiment import Experiment
from experimentarchiver.state import ExperimentState, write_json, read_json


logger = logging.getLogger(__name__)


def split_archive_and_experiment_name(path):
    if os.path.isabs(path):
        raise Exception('Only relative paths allowed')
    parts = os_utils.split_all_parts(path)
    parts = [p for p in parts if p != '']
    if len(parts) != 2:
        raise Exception('Only paths with exactly 2 parts are allowed')
    return parts


class ExperimentArchiver:

    def __init__(self, archive_name):
        self._archiveName = archive_name
        options_file = os.path.join(archive_name, 'project.ini')
        self._project = Project(options_file)

    def find_free_experiment_name(self, raw_name):
        today = date.today().strftime('%Y%m%d')   
        number = -1
        experiment_path = ''
        experiment_name = ''
        while experiment_path == '' or os.path.isdir(experiment_path):
            number += 1
            experiment_name = "{0}_{1}_{2:02d}".format(today, raw_name, number)
            experiment_path = os.path.join(self._archiveName, experiment_name)
        return experiment_name

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
            logger.debug('Writing command status to %s', self._project.path('last-command'))
            write_json(command_record, self._project.path('last-command'))
        if command_record['status'] != 0:
            logger.warning('Command exited with non-zero status: %s', command_record['status'])
        else:
            logger.info('Successfully executed the command.')
        return command_record

    def run_last_command(self):
        logger.info('Trying recorded run, using last recorded command.')
        last_command_record = self._project.path('last-command')
        try:
            command_record = read_json(last_command_record)
        except IOError:
            logger.error('Could not find a record of the last command in %s', last_command_record)
            logger.error('Nothing will be run.')
        else:
            if command_record['status'] != 0:
                logger.warning('Running a recorded command with non-zero exit status: %s', command_record['status'])
            return self._run_and_record(command_record['command'])
    
    def run(self, command):
        logger.info('Trying recorded run, using specified command.')
        return self._run_and_record(command)

    def archive(self, raw_name):
        logger.info('Archiving experiment for project %s', self._archiveName)
        experiment_name = self.find_free_experiment_name(raw_name)
        logger.info('Experiment name is %s', experiment_name)
        experiment = Experiment(self._archiveName, experiment_name)
        experiment.archive_project(self._project)

    def restore(self, experiment_name):
        logger.info('Restoring experiment %s to project %s', experiment_name, self._archiveName)
        experiment = Experiment(self._archiveName, experiment_name)
        self._project.restore_to_project(experiment)
    
    def run_and_archive(self, raw_name, command):
        self.run(command)
        self.archive(raw_name)
    
    def restore_and_run(self, experiment_name):
        self.restore(experiment_name)
        self.run_last_command()
