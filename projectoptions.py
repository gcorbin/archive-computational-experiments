import configparser
import os

class ProjectOptions:

    def __init__(self, optionsFileName):
        self._config = configparser.ConfigParser(interpolation = configparser.ExtendedInterpolation())
        self._config.read(optionsFileName) 

    def path(self,key):
        return self._config['paths'][key]

    def option(self,key):
        return self._config['options'][key]
