import argparse
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONAL_DIR = os.path.join(BASE_DIR, 'personal')

def run_command(args, cwd=None, show_commands=False):
    kwargs = {'check': True}
    if cwd is not None:
        kwargs['cwd'] = cwd
    if show_commands:
        print('\x1b[1m{}\x1b[m'.format(' '.join(args)))
    else:
        kwargs['stderr'] = subprocess.DEVNULL
        kwargs['stdout'] = subprocess.DEVNULL
    return subprocess.run(args, **kwargs)

def add(package, show_commands=False):
    url = ('https://aur.archlinux.org/cgit/aur.git/snapshot'
           '/{}.tar.gz').format(package)
    wget_args = ['wget', url]
    run_command(wget_args, cwd=PERSONAL_DIR, show_commands=show_commands)

    package_snapshot = os.path.join(PERSONAL_DIR, '{}.tar.gz'.format(package))
    tar_args = ['tar', 'xzvf', package_snapshot]
    run_command(tar_args, cwd=PERSONAL_DIR, show_commands=show_commands)

    rm_args = ['rm', '-f', package_snapshot,
               os.path.join(PERSONAL_DIR, package, '.SRCINFO')]
    run_command(rm_args, cwd=PERSONAL_DIR, show_commands=show_commands)

def main(args):
    parser = argparse.ArgumentParser(description='AUR Manager')
    parser.add_argument('--show-commands', action='store_true')
    parser.add_argument('action', choices=['add'])
    parser.add_argument('packages', nargs=argparse.REMAINDER)
    parsed_args = parser.parse_args()
    if parsed_args.action == 'add':
        for package in parsed_args.packages:
            add(package, show_commands=parsed_args.show_commands)
