import sys
import os
import copy
import subprocess
from datetime import date
import logging

import Beholding.os_utils as os_utils
from Beholding.project import Project
from Beholding.casefile import Casefile


logger = logging.getLogger(__name__)


class Archivist:

    def __init__(self, archive_name):
        self._archiveName = archive_name
        options_file = os.path.join(archive_name, 'project.ini')
        self._project = Project(options_file)

    def update_options(self, options):
        self._project.update_options(options)

    def _get_path_to_casefile(self, cabinet_name, casefile_path):
        if cabinet_name != '':
            casefile_path = os.path.join('data', casefile_path)
        return os.path.join(cabinet_name, casefile_path)

    def _get_path_to_cabinet(self, cabinet_name):
        return os.path.join(self._archiveName, cabinet_name)

    def _check_if_cabinet_exists(self, cabinet_name):
        cabinet_path = self._get_path_to_cabinet(cabinet_name)
        if cabinet_name == '':
            return True
        return os.path.isfile(os.path.join(cabinet_path, 'cabinet-description'))

    def _find_free_casefile_path(self, cabinet_name, raw_path):
        head, raw_name = os.path.split(raw_path)

        today = date.today().strftime('%Y%m%d')
        number = -1
        full_casefile_path = ''
        casefile_path = ''
        while full_casefile_path == '' or os.path.isdir(full_casefile_path):
            number += 1
            casefile_name = "{0}_{1}_{2:02d}".format(today, raw_name, number)
            casefile_path = os.path.join(head, casefile_name)
            casefile_path = self._get_path_to_casefile(cabinet_name, casefile_path)
            full_casefile_path = os.path.join(self._archiveName, casefile_path)
        return casefile_path

    def _run_and_record(self, command):
        command_record = {'status': 1, 'command': command}
        self._project.take_output_snapshot()
        try:
            with os_utils.ChangedDirectory(self._project.path('build-path')):
                extra_args = self._project.option('append-arguments')
                augmented_command = copy.copy(command_record['command'])
                augmented_command.extend(extra_args)
                logger.debug('Executing command %s', augmented_command)
                if self._project.option('do-record-console'):
                    with open(self._project.path('console-log'), 'w') as logfile:
                        proc = subprocess.Popen(augmented_command, stdout=subprocess.PIPE, universal_newlines=False)
                        # this mess is necessary to handle '\r' characters correctly in the console output 
                        # universal_newlines=True would translate '\r' to '\n'
                        # which would spam the console 
                        #
                        # the readline() method only recongnises '\n' characters
                        # therefore, we read the output in small chunks, and 
                        # detect both '\r' and '\n' manually
                        buf = ''
                        line = proc.stdout.readline(80) 
                        buf = buf + line
                        while line != b'':
                            ri = max(buf.rfind('\n'), buf.rfind('\r'))
                            if ri > 0: 
                                buf_left = buf[:ri+1]
                                buf = buf[ri+1:]
                                sys.stdout.write(buf_left)
                                logfile.write(buf_left)
                            line = proc.stdout.readline(80)
                            buf = buf + line
                        sys.stdout.write(buf)
                        logfile.write(buf)
                        proc.stdout.close()
                        command_record['status'] = proc.wait()
                else:
                    command_record['status'] = subprocess.call(augmented_command)
        finally:
            self._project.record_command(command_record)
            if command_record['status'] != 0:
                logger.warning('Command exited with non-zero status: %s', command_record['status'])
            else:
                logger.info('Successfully executed the command.')
            self._project.take_output_snapshot()
            self._project.record_output_changes()

        return command_record

    def replay(self):
        logger.info('Trying recorded run, using last recorded command.')
        command_record = self._project.read_command()
        if len(command_record['command']) > 0:
            if command_record['status'] != 0:
                logger.warning('Running a recorded command with non-zero exit status: %s', command_record['status'])
            return self._run_and_record(command_record['command'])
        else:
            logger.error('Nothing will be run.')
            return command_record

    def record(self, command):
        self._project.build_project()
        logger.info('Trying recorded run, using specified command.')
        return self._run_and_record(command)

    def create_new_filecabinet(self, cabinet_name, description=''):
        logger.info('Creating new file cabinet %s for project %s', cabinet_name, self._archiveName)
        cabinet_path = self._get_path_to_cabinet(cabinet_name)
        if os.path.isdir(cabinet_path):
            logger.warning('Cannot use an existing folder %s to create a new cabinet.', cabinet_path)
            return
        os_utils.make_directory_if_nonexistent(cabinet_path)

        doc_path = os.path.join(cabinet_path, 'doc')
        os_utils.make_directory_if_nonexistent(doc_path)
        os_utils.make_directory_if_nonexistent(os.path.join(cabinet_path, 'data'))

        protocol_template = os.path.join(self._archiveName, 'protocol_template.tex')
        if os.path.isfile(protocol_template):
            os_utils.copy_files(self._archiveName, doc_path, ['protocol_template.tex'])
        else:
            logger.warning('The file %s does not exist. '
                           'Consider writing a template for experiment protocols. ', protocol_template)
        with open(os.path.join(doc_path, 'protocol_macros.tex'), 'w') as f:
            f.write('\\newcommand{\\protocoltitle}{%s}\n' % (cabinet_name,))
            f.write('\\newcommand{\\protocoldate}{%s}\n' % (date.today().strftime('%d.%m.%Y'), ))
            f.write('\\newcommand{\\protocoldescription}{%s}\n' % (description, ))

        with open(os.path.join(cabinet_path, 'cabinet-description'), 'w') as f:
            f.write(description)

    def archive(self, cabinet_name, raw_name, description=''):
        logger.info('Archiving statement for archive %s', self._archiveName)
        if not self._check_if_cabinet_exists(cabinet_name) :
            raise Exception('There is no valid file cabinet with the name {0}'.format(cabinet_name))
        casefile_path = self._find_free_casefile_path(cabinet_name, raw_name)
        logger.info('Case file name is %s', casefile_path)
        experiment = Casefile(self._archiveName, casefile_path)
        experiment.archive_project(self._project, description)

    def remember(self, casefile_path):
        logger.info('Restoring case file %s to project %s', casefile_path, self._archiveName)
        experiment = Casefile(self._archiveName, casefile_path)
        self._project.restore_to_project(experiment)