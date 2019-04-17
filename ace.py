#!/usr/bin/python

import os
import sys
import argparse
import logging
import experimentarchiver.os_utils as os_utils
from experimentarchiver.archiver import ExperimentArchiver, split_archive_and_experiment_name
from experimentarchiver.defaultlogger import set_default_logging_behavior

logger = logging.getLogger('experimentarchiver.main')


def make_command_list(command_str):
    return command_str.split(' ')


def split_experiment_sub_path(archive_name, experiment_path):
    archive_name_from_experiment, experiment_sub_path = split_archive_and_experiment_name(experiment_path)
    if not archive_name_from_experiment == os.path.normpath(archive_name):
        experiment_sub_path = experiment_path
    return experiment_sub_path


if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser()
    parent_parser.add_argument('archive', help='Which archive to work on.')

    main_parser = argparse.ArgumentParser(description='Archive computational experiments')
    subparsers = main_parser.add_subparsers(dest='mode', title='Subcommands',
                                            description='Select one of the following operations: ')

    run_parser = subparsers.add_parser('run', parents=[parent_parser], conflict_handler='resolve',
                                       help='Run a command in the project build directory and record it.')
    run_parser.add_argument('command', help='The command line argument to run. '
                                            'Put multiple arguments in a quoted string')

    rerun_parser = subparsers.add_parser('rerun', parents=[parent_parser], conflict_handler='resolve',
                                         help='Run the last recorded command.')

    new_set_parser = subparsers.add_parser('new-set', parents=[parent_parser], conflict_handler='resolve',
                                           help='Create a new sub-folder and templates'
                                                ' for a set of related experiments')
    new_set_parser.add_argument('set', help='The name of the sub-folder')
    new_set_parser.add_argument('-d', '--description', help='Summarize the goal of this set of experiments', default='')

    archive_parser = subparsers.add_parser('archive', parents=[parent_parser], conflict_handler='resolve',
                                           help='Save the current project state in the archive.')
    archive_parser.add_argument('name', help='A descriptive name for the experiment. '
                                             'The experiment will be stored under <date>_<name>_<number>')
    archive_parser.add_argument('-d', '--description', help='Describe your experiment here in a few words. '
                                                            'Use #tag s to help you find an experiment later')
    archive_parser.add_argument('-s', '--set', help='The experiment set to use.', default='')

    restore_parser = subparsers.add_parser('restore', parents=[parent_parser], conflict_handler='resolve',
                                           help='Restore an experiment to the project.')
    restore_parser.add_argument('experiment', help='Relative path to the experiment folder')

    restore_and_run_parser = subparsers.add_parser('restore-and-run', parents=[parent_parser],
                                                   conflict_handler='resolve',
                                                   help='Restore an experiment to the project and run it.')
    restore_and_run_parser.add_argument('experiment', help='Relative path to the experiment folder')

    run_and_archive_parser = subparsers.add_parser('run-and-archive', parents=[archive_parser],
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

        archiver = ExperimentArchiver(args.archive)

        if args.mode == 'run':
            archiver.run(make_command_list(args.command))
        elif args.mode == 'rerun':
            archiver.run_last_command()
        elif args.mode == 'new-set':
            archiver.create_new_set(args.set, args.description)
        elif args.mode == 'archive':
            experiment_name = split_experiment_sub_path(args.archive, args.name)
            archiver.archive(args.set, experiment_name, args.description)
        elif args.mode == 'restore':
            experiment_name = split_experiment_sub_path(args.archive, args.experiment)
            archiver.restore(experiment_name)
        elif args.mode == 'restore-and-run':
            experiment_name = split_experiment_sub_path(args.archive, args.experiment)
            archiver.restore(experiment_name)
            archiver.run_last_command()
        elif args.mode == 'run-and-archive':
            experiment_name = split_experiment_sub_path(args.archive, args.name)
            archiver.run(make_command_list(args.command))
            archiver.archive(args.set, experiment_name, args.description)
        else:
            raise Exception('Unrecognised mode : {0}'.format(args.mode))

    except Exception as ex:
        logger.critical('', exc_info=ex)
        sys.exit(1)

    sys.exit(0)
