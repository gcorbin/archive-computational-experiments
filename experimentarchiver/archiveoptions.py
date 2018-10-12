import os

class ArchiveOptions:
    
    def __init__(self, archivePath, experimentName):
        experimentPath = os.path.join(archivePath,experimentName)
        self._paths = {'archive-path':archivePath,
                       'experiment-path':experimentPath,
                       'parameter-path':os.path.join(experimentPath,'parameters/'),
                       'parameter-list':os.path.join(experimentPath,'parameters/parameter-list'),
                       'commit-hash':os.path.join(experimentPath,'commit-hash'),
                       'last-command':os.path.join(experimentPath,'last-command'),
                       'input-files':os.path.join(experimentPath,'input-files')}

    def path(self,key):
        return self._paths[key]
