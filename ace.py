#!/usr/bin/python

import os
import sys
import argparse
from experimentarchiver.archiver import ExperimentArchiver, split_archive_and_experiment_name
from experimentarchiver.defaultlogger import set_default_logging_behavior


def make_command_list(command_str):
    return command_str.split(' ')


def get_experiment_name(archive_name, experiment_path):
    archive_name_from_experiment, experiment_name = split_archive_and_experiment_name(experiment_path)
    if not archive_name_from_experiment == os.path.normpath(archive_name):
        raise Exception('Archive names do not match: {0} != {1}'
                        .format(archive_name_from_experiment, os.path.normpath(archive_name)))
    return experiment_name


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

    archive_parser = subparsers.add_parser('archive', parents=[parent_parser], conflict_handler='resolve',
                                           help='Save the current project state in the archive.')
    archive_parser.add_argument('name', help='A descriptive name for the experiment. '
                                             'The experiment will be stored under <date>_<name>_<number>')
    archive_parser.add_argument('-d', '--description', help='Describe your experiment here in a few words. '
                                                            'Use #tag s to help you find an experiment later')

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

    set_default_logging_behavior(logfile=args.mode)
    archiver = ExperimentArchiver(args.archive)

    if args.mode == 'run':
        archiver.run(make_command_list(args.command))
    elif args.mode == 'rerun':
        archiver.run_last_command()
    elif args.mode == 'archive':
        experiment_name = get_experiment_name(args.archive, args.name)
        archiver.archive(experiment_name, args.description)
    elif args.mode == 'restore':
        experiment_name = get_experiment_name(args.archive, args.experiment)
        archiver.restore(experiment_name)
    elif args.mode == 'restore-and-run':
        experiment_name = get_experiment_name(args.archive, args.experiment)
        archiver.restore_and_run(experiment_name)
    elif args.mode == 'run-and-archive':
        experiment_name = get_experiment_name(args.archive, args.name)
        archiver.run_and_archive(experiment_name, make_command_list(args.command))
    else:
        raise Exception('Unrecognised mode : {0}'.format(args.mode))

    sys.exit(0)
