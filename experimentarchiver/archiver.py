import os
import copy
import shutil
import subprocess
from datetime import date
import logging

import experimentarchiver.os_utils as os_utils
from experimentarchiver.projectoptions import ProjectOptions
from experimentarchiver.archiveoptions import ArchiveOptions
from experimentarchiver.state import ExperimentState, write_json

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
        self._projectOptions = ProjectOptions(options_file)
        self._logger = None

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
    
    def run_and_record(self, command):
        command_record = {'status': 1, 'command': command}
        try:
            with os_utils.ChangedDirectory(self._projectOptions.path('build-path')):
                extra_args = self._projectOptions.option('append-arguments')
                augmented_command = copy.copy(command)
                augmented_command.extend(extra_args)
                command_record['status'] = subprocess.call(augmented_command)
        finally:
            write_json(command_record, self._projectOptions.path('last-command'))
        return command_record

    def archive(self, raw_name):
        experiment_name = self.find_free_experiment_name(raw_name)
        archive_opts = ArchiveOptions(self._archiveName, experiment_name)
        state = ExperimentState(self._projectOptions, archive_opts)
        state.read_from_project()
        try:
            state.write_to_archive()
        except:
            shutil.rmtree(archive_opts.path('experiment-path'), ignore_errors=True)
            raise
        return state

    def restore(self, experiment_name):
        archive_opts = ArchiveOptions(self._archiveName, experiment_name)
        state = ExperimentState(self._projectOptions, archive_opts)
        state.read_from_archive()
        state.restore_to_project()
        return state
    
    def run_and_archive(self, raw_name, command):
        self.run_and_record(command)
        state = self.archive(raw_name)
        return state
    
    def restore_and_run(self, experiment_name):
        state = self.restore(experiment_name)
        command = state.get_command()['command']
        self.run_and_record(command)
        state.update_command_status()
        return state
