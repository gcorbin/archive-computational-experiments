
import os
from datetime import date

class ArchiveOptions:
    
    def __init__(self, archivePath, experimentName=''):
        experimentPath = ''
        if experimentName == '':
            experimentPath = self.find_free_experiment_path(archivePath,experimentName)
        else:
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
    
    def find_free_experiment_path(self,archivePath,rawName):
        today = date.today().strftime('%Y%m%d')   
        number = -1
        experimentPath = ''
        while experimentPath == '' or os.path.isdir(experimentPath) :
            number += 1
            experimentName = "{0}_{1}_{2:02d}".format(today, rawName, number)
            experimentPath = os.path.join(archivePath,experimentName)
        return experimentPath
            