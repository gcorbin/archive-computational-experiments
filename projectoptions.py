import configparser
import os

class ProjectOptions:

    def __init__(self, optionsFileName):
        config = configparser.ConfigParser(interpolation = configparser.ExtendedInterpolation())
        config.read(optionsFileName) 
        
        self._options = {}
        self._options['do-git-checkout'] = config.getboolean('options', 'do-git-checkout', fallback=False)
        self._options['do-build'] = config.getboolean('options', 'do-build', fallback=False)
        if self._options['do-build']:
            self._options['build-command'] = config.get('options','build-command')
        else:
            self._options['build-command'] = ''
        self._options['hash-algorithm'] = config.get('options','hash-algorithm',fallback='sha256')
        
        self._paths = {}
        for key in ['git-path', 'top-path', 'build-path', 'input-data-path',
                    'output-data-path', 'parameter-list', 'last-command', 
                    'get-input-files']:
            self._paths[key] = config.get('paths',key)

    def path(self,key):
        return self._paths[key]

    def option(self,key):
        return self._options[key]
