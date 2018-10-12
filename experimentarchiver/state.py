import os
import hashlib
import json
import subprocess
import imp

from projectoptions import ProjectOptions
from archiveoptions import ArchiveOptions
import experimentarchiver.os_utils as os_utils
import experimentarchiver.git_utils as git_utils


def compute_file_hash(filename, hash_algorithm):
    file_hash = hashlib.new(hash_algorithm)
    
    buffer_size = 64 * pow(2, 10)  # 64 kilobytes
    with open(filename, 'rb') as file_to_hash:
        while True:
            chunk = file_to_hash.read(buffer_size)
            if not chunk:
                break
            file_hash.update(chunk)
        
    return "{0}".format(file_hash.hexdigest())


def read_lines_into_list(filename):
    with open(filename, 'r') as f:
        line_list = [line.strip() for line in f]
    return line_list


def get_paths_to_input_data(path_to_script):
    imported_module = imp.load_source('tmp_script_module', path_to_script)
    execute_path = os.path.dirname(path_to_script)
    with os_utils.ChdirContext(execute_path):
        path_list = imported_module.getFilesToHash()
    return path_list


def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


class ExperimentState:

    def __init__(self, project_opts, archive_opts):
        self._projectOptions = project_opts
        self._archiveOptions = archive_opts
        self._commitHash = ''
        self._pathsToParameters = []
        self._inputData = []
        self._pathsToOutputData = []
        self._command = []
        self._environment = None
        
    def _hash_input_data(self):
        relative_paths_to_input_data = get_paths_to_input_data(self._projectOptions.path('get-input-files'))
        hash_algorithm = self._projectOptions.option('hash-algorithm')
        data = []
        for relpath in relative_paths_to_input_data:
            abspath = os.path.join(self._projectOptions.path('input-data-path'), relpath)
            file_hash = compute_file_hash(abspath, hash_algorithm)
            hash_tuple = (relpath, hash_algorithm, file_hash)
            data.append(hash_tuple)
        return data

    def _verify_hashes(self):
        for (relpath, hash_algorithm, stored_hash) in self._inputData:
            abspath = os.path.join(self._projectOptions.path('input-data-path'), relpath)
            computed_hash = compute_file_hash(abspath, hash_algorithm)
            if stored_hash != computed_hash:
                raise Exception("The stored and computed {0} hashes for the file {1} differ: {2} != {3}"
                                .format(hash_algorithm, abspath, stored_hash, computed_hash))

    def _build_project(self):
        build_command = self._projectOptions.option('build-command').strip().split()
        with os_utils.ChdirContext(self._projectOptions.path('build-path')):
            subprocess.check_call(build_command)
            
    def get_command(self):
        return self._command
    
    def update_command_status(self):
        self._command = read_json(self._projectOptions.path('last-command'))

    def read_from_project(self):
        self._commitHash = git_utils.get_git_commit_hash(self._projectOptions.path('git-path'))
        self._pathsToParameters = read_lines_into_list(self._projectOptions.path('parameter-list'))
        repo_is_clean = git_utils.is_git_repo_clean(self._projectOptions.path('git-path'),
                                                    self._projectOptions.path('top-path'),
                                                    self._pathsToParameters)
        if not repo_is_clean:
            raise Exception('The git repository contains unstaged or uncommitted changes')
        self._inputData = self._hash_input_data()
        self._pathsToOutputData = []  # not yet implemented
        self._command = read_json(self._projectOptions.path('last-command'))
        self._environment = None  # not yet implemented

    def restore_to_project(self):
        paths_to_parameters = read_lines_into_list(self._projectOptions.path('parameter-list'))
        repo_is_clean = git_utils.is_git_repo_clean(self._projectOptions.path('git-path'),
                                                    self._projectOptions.path('top-path'),
                                                    paths_to_parameters)
        if not repo_is_clean:
            raise Exception('The git repository contains unstaged or uncommitted changes')
        git_utils.checkout_git_commit(self._projectOptions.path('git-path'), self._commitHash)
        os_utils.copy_files(self._archiveOptions.path('parameter-path'),
                            self._projectOptions.path('top-path'),
                            self._pathsToParameters,
                            create_directories=False)
        # nothing to do for input data
        # output data not implemented
        write_json(self._command, self._projectOptions.path('last-command'))
        # environment not implemented 
        if self._projectOptions.option('do-build'):
            self._build_project()

    def read_from_archive(self):
        self._commitHash = read_json(self._archiveOptions.path('commit-hash'))
        self._pathsToParameters = read_json(self._archiveOptions.path('parameter-list'))
        self._inputData = read_json(self._archiveOptions.path('input-files')) 
        self._verify_hashes()
        self._pathsToOutputData = []  # not yet implemented
        self._command = read_json(self._archiveOptions.path('last-command'))
        self._environment = None  # not yet implemented

    def write_to_archive(self):
        os_utils.make_directory_if_nonexistent(self._archiveOptions.path('archive-path'))
        os_utils.make_directory_if_nonexistent(self._archiveOptions.path('experiment-path'))
        write_json(self._commitHash, self._archiveOptions.path('commit-hash')) 
        os_utils.make_directory_if_nonexistent(self._archiveOptions.path('parameter-path'))
        write_json(self._pathsToParameters, self._archiveOptions.path('parameter-list'))
        os_utils.copy_files(self._projectOptions.path('top-path'),
                            self._archiveOptions.path('parameter-path'),
                            self._pathsToParameters,
                            create_directories=True)
        write_json(self._inputData, self._archiveOptions.path('input-files'))
        # output data not yet implemented
        write_json(self._command, self._archiveOptions.path('last-command'))
        # environment not yet implemented
