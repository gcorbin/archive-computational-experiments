import json
import logging

logger = logging.getLogger(__name__)


def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


class Statement:

    def __init__(self):
        self.commitHash = ''
        self.pathsToParameters = []
        self.inputData = []
        self.command = []
        self.environment = None
        self.description = ''
        self.pathsToOutputData = []
