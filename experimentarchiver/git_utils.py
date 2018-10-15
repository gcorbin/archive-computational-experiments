import os
from subprocess import check_call, check_output
import logging


logger = logging.getLogger(__name__)


def make_git_diff_exclude_list(excludelist):
    modifiedlist = []
    for item in excludelist:
        modifiedlist.append("':(exclude){0}'".format(item))
    return modifiedlist


def is_git_repo_clean(path_to_repo, path_to_project, excludelist):
    logger.info('Checking if the git repository is clean.')
    logger.debug('... repo path: %s', path_to_repo)
    command = ['git', '-C', path_to_project, 'diff', 'HEAD', '--quiet', '--', path_to_repo]
    for item in make_git_diff_exclude_list(excludelist):
        command.append(item)
    commandstr = ''
    for arg in command:
        commandstr = commandstr + ' ' + arg
    logger.debug('... executing command: %s', commandstr)
    # somehow the subprocess.call method does not work here
    # todo: check if using call with the shell=True argument will work
    status = os.system(commandstr)
    return status == 0


def get_git_commit_hash(path_to_repo):
    logger.info('Retrieving Commit hash from repository.')
    logger.debug('... repo path: %s', path_to_repo)
    command = ['git', '-C', path_to_repo, 'rev-parse', 'master']
    logger.debug('... executing command %s', str(command))
    commithash = check_output(command)
    # In Python 3 the check_output function returns a byte-array,
    # that has to be converted to a string
    commithash = commithash.decode('utf-8')
    commithash = commithash.strip('\n').strip()
    return commithash


def checkout_git_commit(path_to_repo, commithash):
    logger.info('Checking out git repository.')
    logger.debug('... repo path: %s', path_to_repo)
    command = ['git', '-C', path_to_repo, 'checkout', commithash]
    logger.debug('... executing command %s', str(command))
    check_call(command)
