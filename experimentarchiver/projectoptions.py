import configparser


class ProjectOptions:

    def __init__(self, options_file_name):
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(options_file_name)
        
        self._options = {}
        self._options['do-git-checkout'] = config.getboolean('options', 'do-git-checkout', fallback=False)
        self._options['do-build'] = config.getboolean('options', 'do-build', fallback=False)
        if self._options['do-build']:
            self._options['build-command'] = config.get('options', 'build-command')
        else:
            self._options['build-command'] = ''
        self._options['hash-algorithm'] = config.get('options', 'hash-algorithm', fallback='sha256')
        extra_args = config.get('options', 'append-arguments', fallback='')
        extra_args = extra_args.strip()
        if extra_args == '':
            self._options['append-arguments'] = []
        else:
            self._options['append-arguments'] = extra_args.split(' ')
        
        self._paths = {}
        for key in ['git-path', 'top-path', 'build-path', 'input-data-path',
                    'output-data-path', 'parameter-list', 'last-command', 
                    'get-input-files']:
            self._paths[key] = config.get('paths', key)

    def path(self, key):
        return self._paths[key]

    def option(self, key):
        return self._options[key]
