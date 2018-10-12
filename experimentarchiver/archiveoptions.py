import os


class ArchiveOptions:
    
    def __init__(self, archive_path, experiment_name):
        experiment_path = os.path.join(archive_path, experiment_name)
        self._paths = {'archive-path': archive_path,
                       'experiment-path': experiment_path,
                       'parameter-path': os.path.join(experiment_path, 'parameters/'),
                       'parameter-list': os.path.join(experiment_path, 'parameters/parameter-list'),
                       'commit-hash': os.path.join(experiment_path, 'commit-hash'),
                       'last-command': os.path.join(experiment_path, 'last-command'),
                       'input-files': os.path.join(experiment_path, 'input-files')}

    def path(self, key):
        return self._paths[key]
