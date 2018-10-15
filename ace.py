#!/usr/bin/python

import os
import sys
import argparse
from experimentarchiver.archiver import ExperimentArchiver, split_archive_and_experiment_name
from experimentarchiver.defaultlogger import set_default_logging_behavior


if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser()
    parent_parser.add_argument('archive', help='Which archive to work on.')

    main_parser = argparse.ArgumentParser(description='Archive computational experiments')
    subparsers = main_parser.add_subparsers(dest='mode', title='Subcommands',
                                            description='Select one of the following operations: ')

    run_parser = subparsers.add_parser('run', parents=[parent_parser], conflict_handler='resolve',
                                       help='Run a command in the project build directory and record it.')
    run_parser.add_argument('command', nargs='+')

    run_parser = subparsers.add_parser('rerun', parents=[parent_parser], conflict_handler='resolve',
                                       help='Run the last recorded command.')

    archive_parser = subparsers.add_parser('archive', parents=[parent_parser], conflict_handler='resolve',
                                           help='Save the current project state in the archive.')
    archive_parser.add_argument('name')
    archive_parser.add_argument('-d', '--description')

    restore_parser = subparsers.add_parser('restore', parents=[parent_parser], conflict_handler='resolve',
                                           help='Restore an experiment to the project.')
    restore_parser.add_argument('experiment')

    restore_and_run_parser = subparsers.add_parser('restore-and-run', parents=[parent_parser],
                                                   conflict_handler='resolve',
                                                   help='Restore an experiment to the project and run it.')
    restore_and_run_parser.add_argument('experiment')

    run_and_archive_parser = subparsers.add_parser('run-and-archive', parents=[archive_parser],
                                                   conflict_handler='resolve',
                                                   help='Run a command and store the experiment to the archive.')
    run_and_archive_parser.add_argument('command', nargs='+')

    args = main_parser.parse_args()

    set_default_logging_behavior(logfile=args.mode)
    archiver = ExperimentArchiver(args.archive)

    if args.mode == 'run':
        archiver.run(args.command)
    elif args.mode == 'rerun':
        archiver.run_last_command()
    elif args.mode == 'archive':
        archiver.archive(args.name, args.description)
    elif args.mode == 'restore':
        archiveName, experimentName = split_archive_and_experiment_name(args.experiment)
        if not archiveName == os.path.normpath(args.archive):
            raise Exception('Archive names do not match: {0} != {1}'
                            .format(archiveName, os.path.normpath(args.archive)))
        archiver.restore(experimentName)
    elif args.mode == 'restore-and-run':
        archiveName, experimentName = split_archive_and_experiment_name(args.experiment)
        if not archiveName == os.path.normpath(args.archive):
            raise Exception('Archive names do not match: {0} != {1}'
                            .format(archiveName, os.path.normpath(args.archive)))
        archiver.restore_and_run(experimentName)
    elif args.mode == 'run-and-archive':
        archiver.run_and_archive(args.name, args.command)
    else:
        raise Exception('Unrecognised mode : {0}'.format(args.mode))

    sys.exit(0)
