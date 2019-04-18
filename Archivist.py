#!/usr/bin/python

import os
import sys
import argparse
import logging
import Beholding.os_utils as os_utils
from Beholding.archivist import Archivist
from Beholding.defaultlogger import set_default_logging_behavior

logger = logging.getLogger('Beholding.main')


def make_command_list(command_str):
    return command_str.split(' ')


def split_casefile_sub_path(archive_name, casefile_path):
    archive_name_from_experiment, casefile_subpath = os_utils.split_path_after_first_component(casefile_path)
    if not archive_name_from_experiment == os.path.normpath(archive_name):
        casefile_subpath = casefile_path
    return casefile_subpath


if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser()
    parent_parser.add_argument('archive', help='Which archive to work on.')

    main_parser = argparse.ArgumentParser(description='Record and archive computational experiments')
    subparsers = main_parser.add_subparsers(dest='mode', title='Subcommands',
                                            description='Select one of the following operations: ')

    run_parser = subparsers.add_parser('record', parents=[parent_parser], conflict_handler='resolve',
                                       help='Run a command in the project build directory and record it.')
    run_parser.add_argument('command', help='The command line argument to run. '
                                            'Put multiple arguments in a quoted string')

    rerun_parser = subparsers.add_parser('replay', parents=[parent_parser], conflict_handler='resolve',
                                         help='Run the last recorded command.')

    new_set_parser = subparsers.add_parser('new-file-cabinet', parents=[parent_parser], conflict_handler='resolve',
                                           help='Create a new sub-folder and templates'
                                                ' for a set of related experiments')
    new_set_parser.add_argument('file_cabinet', help='The name of the sub-folder')
    new_set_parser.add_argument('-d', '--description', help='Summarize the goal of this set of experiments', default='')

    archive_parser = subparsers.add_parser('archive', parents=[parent_parser], conflict_handler='resolve',
                                           help='Save the current project state in the archive.')
    archive_parser.add_argument('name', help='A descriptive name for the experiment. '
                                             'The experiment will be stored under <date>_<name>_<number>')
    archive_parser.add_argument('-d', '--description', help='Describe your experiment here in a few words. '
                                                            'Use #tag s to help you find an experiment later')
    archive_parser.add_argument('-f', '--file-cabinet', help='The experiment set to use.', default='')
    archive_parser.add_argument('--no-outputs', help='This flag supresses copying program outputs to the archive',
                                action='store_true')

    restore_parser = subparsers.add_parser('remember', parents=[parent_parser], conflict_handler='resolve',
                                           help='Restore an experiment to the project.')
    restore_parser.add_argument('experiment', help='Relative path to the experiment folder')

    restore_and_run_parser = subparsers.add_parser('remember-and-replay', parents=[parent_parser],
                                                   conflict_handler='resolve',
                                                   help='Restore an experiment to the project and run it.')
    restore_and_run_parser.add_argument('experiment', help='Relative path to the experiment folder')

    run_and_archive_parser = subparsers.add_parser('record-and-archive', parents=[archive_parser],
                                                   conflict_handler='resolve',
                                                   help='Run a command and store the experiment to the archive.')
    run_and_archive_parser.add_argument('command', help='The command line argument to run. '
                                                        'Put multiple arguments in a quoted string')

    args = main_parser.parse_args()

    set_default_logging_behavior(logfile='ace')

    try:

        if not os.path.isdir(args.archive):
            raise Exception('The archive with name {0} does not exist'.format(args.archive))

        if os_utils.is_composite(args.archive):
            raise Exception('The archive name must not be composite. Got {0}'.format(args.archive))

        archivist = Archivist(args.archive)

        override_options = {}
        if args.mode == 'archive' or args.mode == 'record-and-archive':
            override_options['do-record-outputs'] = not args.no_outputs
        archivist.update_options(override_options)

        if args.mode == 'record':
            archivist.record(make_command_list(args.command))
        elif args.mode == 'replay':
            archivist.replay()
        elif args.mode == 'new-file-cabinet':
            archivist.create_new_filecabinet(args.file_cabinet, args.description)
        elif args.mode == 'archive':
            casefile_name = split_casefile_sub_path(args.archive, args.name)
            archivist.archive(args.file_cabinet, casefile_name, args.description)
        elif args.mode == 'remember':
            casefile_name = split_casefile_sub_path(args.archive, args.experiment)
            archivist.remember(casefile_name)
        elif args.mode == 'remember-and-replay':
            casefile_name = split_casefile_sub_path(args.archive, args.experiment)
            archivist.remember(casefile_name)
            archivist.replay()
        elif args.mode == 'record-and-archive':
            casefile_name = split_casefile_sub_path(args.archive, args.name)
            archivist.record(make_command_list(args.command))
            archivist.archive(args.set, casefile_name, args.description)
        else:
            raise Exception('Unrecognised mode : {0}'.format(args.mode))

    except Exception as ex:
        logger.critical('', exc_info=ex)
        sys.exit(1)

    sys.exit(0)
