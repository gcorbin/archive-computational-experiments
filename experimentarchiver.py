import os
import copy
import shutil
import subprocess
from datetime import date

from projectoptions import ProjectOptions
from archiveoptions import ArchiveOptions
import os_utils
import git_utils
from  experimentstate import ExperimentState, read_json, write_json


def split_archive_and_experiment_name(path):
    if os.path.isabs(path):
        raise Exception('Only relative paths allowed')
    parts = os_utils.split_all_parts(path)
    parts = [p for p in parts if p != '']
    if len(parts) != 2:
        raise Exception('Only paths with exactly 2 parts are allowed')
    return parts

class ExperimentArchiver:

    def __init__(self, archiveName):
        self._archiveName = archiveName
        optionsFile = os.path.join(archiveName,'project.ini')
        self._projectOptions = ProjectOptions(optionsFile)
        self._logger = None

    def find_free_experiment_name(self,rawName):
        today = date.today().strftime('%Y%m%d')   
        number = -1
        experimentPath = ''
        experimentName = ''
        while experimentPath == '' or os.path.isdir(experimentPath) :
            number += 1
            experimentName = "{0}_{1}_{2:02d}".format(today, rawName, number)
            experimentPath = os.path.join(self._archiveName,experimentName)
        return experimentName
    
    def run_and_record(self,command):
        savePath = os.getcwd()
        commandStatus = {'status':1,'command':command}
        try:
            os.chdir(self._projectOptions.path('build-path'))
            extraArgs = self._projectOptions.option('append-arguments')
            augmentedCommand = copy.copy(command)
            augmentedCommand.extend(extraArgs)
            commandStatus['status'] = subprocess.call(augmentedCommand)
        finally:
            os.chdir(savePath)
            write_json(commandStatus,
                       self._projectOptions.path('last-command'))
        return commandStatus

    def archive(self,rawName):
        experimentName = self.find_free_experiment_name(rawName)
        archiveOptions = ArchiveOptions(self._archiveName,experimentName)
        state = ExperimentState(self._projectOptions,archiveOptions)
        state.read_from_project()
        try:
            state.write_to_archive()
        except:
            shutil.rmtree(archiveOptions.path('experiment-path'),ignore_errors=True)
            raise
        return state

    def restore(self,experimentName):
        archiveOptions = ArchiveOptions(self._archiveName,experimentName)
        state = ExperimentState(self._projectOptions,archiveOptions)
        state.read_from_archive()
        state.restore_to_project()
        return state
    
    def run_and_archive(self,rawName,command):
        self.run_and_record(command)
        state = self.archive(rawName)
        return state
    
    def restore_and_run(self,experimentName):
        state = self.restore(experimentName)
        command = state.get_command()['command']
        commandStatus = self.run_and_record(command)
        state.update_command_status()
        return state
    